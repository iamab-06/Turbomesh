from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import argparse
import os
import asyncio
import time

from core.network import get_lan_ip
from core.hardware import get_hardware_info
from core.auth import auth_manager, get_current_client, security
from core.jobs import job_manager, STORAGE_DIR
from core.worker import process_job

app = FastAPI(title='TurboMesh Host')
templates = Jinja2Templates(directory='templates')

host_ip = get_lan_ip()
hardware_info = get_hardware_info()

class PairRequest(BaseModel): pairing_code: str; client_id: str; device_name: str; os: str; app_version: str
class JobCreateRequest(BaseModel): operation: str
class FinalizeUploadRequest(BaseModel): filename: str; total_chunks: int; expected_size: int; expected_sha256: str

@app.get('/')
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name='dashboard.html', context={'host_ip': host_ip, 'port': getattr(request.app.state, 'port', 8000), 'hardware': hardware_info, 'pairing_code': auth_manager.get_pairing_code()})

@app.post('/api/auth/pair')
async def pair_device(req: PairRequest): return auth_manager.receive_pairing_request(req.pairing_code, req.dict())

@app.get('/api/auth/status')
async def auth_status(client_id: str):
    if client_id in auth_manager.approved_clients: return {'status': 'approved', 'token': auth_manager.approved_clients[client_id]['token']}
    elif client_id in auth_manager.rejected_requests: return {'status': 'rejected'}
    elif client_id in auth_manager.pending_requests: return {'status': 'pending'}
    else: raise HTTPException(status_code=404, detail='Status not found')

@app.post('/api/clients/{client_id}/approve')
async def approve_client(client_id: str): return auth_manager.approve_client(client_id)

@app.post('/api/clients/{client_id}/reject')
async def reject_client(client_id: str): return auth_manager.reject_client(client_id)

@app.post('/api/clients/{client_id}/revoke')
async def revoke_client(client_id: str): return auth_manager.revoke_client(client_id)

@app.get('/api/clients')
async def list_clients(): return {'pending': auth_manager.pending_requests, 'approved': auth_manager.approved_clients}

@app.get('/api/host/info')
async def get_host_info(): return {'ip': host_ip, 'hardware': hardware_info}

@app.post('/api/jobs')
async def create_job(req: JobCreateRequest, client_id: str = Depends(get_current_client)): return job_manager.create_job(client_id, req.operation)

@app.get('/api/jobs/{job_id}')
async def get_job(job_id: str, client_id: str = Depends(get_current_client)): return job_manager.get_job(job_id, client_id)

@app.post('/api/jobs/{job_id}/upload/chunk')
async def upload_chunk(job_id: str, chunk_index: int = Form(...), filename: str = Form(...), file: UploadFile = File(...), client_id: str = Depends(get_current_client)):
    data = await file.read()
    return job_manager.save_chunk(job_id, client_id, filename, chunk_index, data)

@app.post('/api/jobs/{job_id}/upload/finalize')
async def finalize_upload(job_id: str, req: FinalizeUploadRequest, background_tasks: BackgroundTasks, client_id: str = Depends(get_current_client)):
    res = job_manager.finalize_upload(job_id, client_id, req.filename, req.total_chunks, req.expected_size, req.expected_sha256)
    job = job_manager.get_job(job_id, client_id)
    # Check if ready
    required = 2 if job['operation'] == 'image_similarity' else 1
    if len(job['files']) == required:
        job['status'] = 'UPLOAD_COMPLETE'
        background_tasks.add_task(process_job, job_id)
    return res

@app.get('/api/jobs/{job_id}/result/{filename}')
async def download_result(job_id: str, filename: str, client_id: str = Depends(get_current_client)):
    job = job_manager.get_job(job_id, client_id)
    if job['status'] != 'COMPLETED': raise HTTPException(status_code=400, detail='Job not completed')
    path = os.path.join(STORAGE_DIR, job_id, 'output', filename)
    if not os.path.exists(path): raise HTTPException(status_code=404, detail='Result file not found')
    return FileResponse(path)

@app.websocket('/ws/jobs/{job_id}')
async def job_websocket(websocket: WebSocket, job_id: str, token: str):
    await websocket.accept()
    try:
        client_id = auth_manager.verify_token(token)
        job = job_manager.get_job(job_id, client_id)
        while True:
            await websocket.send_json({'job_id': job['job_id'], 'status': job['status'], 'progress': job['progress'], 'stage': job['stage'], 'result_files': job.get('result_files', [])})
            if job['status'] in ['COMPLETED', 'FAILED', 'CANCELLED']: break
            await asyncio.sleep(1)
    except Exception as e:
        await websocket.send_json({'error': str(e)})
    finally:
        await websocket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run TurboMesh Host')
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run('main:app', host=args.host, port=args.port, reload=False)

