from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import argparse
from core.client import tm_client
import httpx
import hashlib
import asyncio
import os

app = FastAPI(title='TurboMesh User')
templates = Jinja2Templates(directory='templates')

class PairRequest(BaseModel):
    host_ip: str
    port: int
    pairing_code: str

class JobCreateReq(BaseModel):
    operation: str

class FinalizeReq(BaseModel):
    filename: str
    total_chunks: int
    expected_size: int
    expected_sha256: str

@app.get('/')
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name='dashboard.html', context={'client': tm_client})

@app.post('/api/pair')
async def pair(req: PairRequest):
    try:
        return await tm_client.request_pairing(req.host_ip, req.port, req.pairing_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/api/status')
async def status():
    s = await tm_client.check_status()
    info = await tm_client.get_host_info()
    return {'auth': s, 'host': info, 'client_id': tm_client.client_id, 'token': tm_client.token is not None, 'raw_token': tm_client.token}

@app.post('/api/jobs')
async def create_job(req: JobCreateReq):
    if not tm_client.token: raise HTTPException(status_code=401, detail='Not authenticated')
    headers = {'Authorization': f'Bearer {tm_client.token}'}
    async with httpx.AsyncClient() as client:
        res = await client.post(f'{tm_client.host_url}/api/jobs', json={'operation': req.operation}, headers=headers)
        res.raise_for_status()
        return res.json()

@app.post('/api/jobs/{job_id}/upload/chunk')
async def upload_chunk(job_id: str, chunk_index: int = Form(...), filename: str = Form(...), file: UploadFile = File(...)):
    if not tm_client.token: raise HTTPException(status_code=401, detail='Not authenticated')
    data = await file.read()
    headers = {'Authorization': f'Bearer {tm_client.token}'}
    async with httpx.AsyncClient() as client:
        files = {'file': (filename, data, 'application/octet-stream')}
        form_data = {'chunk_index': str(chunk_index), 'filename': filename}
        for attempt in range(3):
            try:
                res = await client.post(f'{tm_client.host_url}/api/jobs/{job_id}/upload/chunk', data=form_data, files=files, headers=headers)
                res.raise_for_status()
                return res.json()
            except Exception:
                if attempt == 2: raise
                await asyncio.sleep(1)

@app.post('/api/jobs/{job_id}/upload/finalize')
async def finalize_upload(job_id: str, req: FinalizeReq):
    if not tm_client.token: raise HTTPException(status_code=401, detail='Not authenticated')
    headers = {'Authorization': f'Bearer {tm_client.token}'}
    async with httpx.AsyncClient() as client:
        res = await client.post(f'{tm_client.host_url}/api/jobs/{job_id}/upload/finalize', json=req.dict(), headers=headers)
        res.raise_for_status()
        return res.json()

@app.get('/api/jobs/{job_id}/result/{filename}')
async def proxy_result(job_id: str, filename: str):
    if not tm_client.token: raise HTTPException(status_code=401, detail='Not authenticated')
    headers = {'Authorization': f'Bearer {tm_client.token}'}
    async def stream_generator():
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', f'{tm_client.host_url}/api/jobs/{job_id}/result/{filename}', headers=headers) as r:
                r.raise_for_status()
                async for chunk in r.aiter_bytes():
                    yield chunk
    return StreamingResponse(stream_generator())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run TurboMesh User')
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8001)
    args = parser.parse_args()
    uvicorn.run('main:app', host=args.host, port=args.port, reload=False)

