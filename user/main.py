from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import uvicorn
import argparse
from core.client import tm_client
import httpx
import hashlib
import asyncio
import os
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np
from PIL import Image
import io
import base64

app = FastAPI(title='TurboMesh User')
templates = Jinja2Templates(directory='templates')

# Global state for loaded models
loaded_model = None  # {'model': model, 'metadata': metadata}

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

class InferenceRequest(BaseModel):
    image_data: list  # Flattened normalized image tensor
    input_size: int
    num_classes: int

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

@app.get('/inference')
async def inference_page(request: Request):
    return templates.TemplateResponse(request=request, name='inference.html', context={'client': tm_client})

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
    return {'auth': s, 'host': info, 'client_id': tm_client.client_id, 'token': tm_client.token is not None, 'raw_token': tm_client.token if tm_client.token else None}

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

@app.post('/api/load-model')
async def load_model_endpoint(model_file: UploadFile = File(...), metadata_file: UploadFile = File(...)):
    """Load a trained hand sign model and metadata"""
    global loaded_model
    
    try:
        # Read files
        model_data = await model_file.read()
        metadata_text = await metadata_file.read()
        
        print(f"Received model file: {len(model_data)} bytes")
        print(f"Received metadata: {len(metadata_text)} bytes")
        
        # Parse metadata
        metadata = json.loads(metadata_text)
        num_classes = metadata['num_classes']
        print(f"Metadata parsed: {num_classes} classes")
        
        # Recreate model architecture (ResNet50)
        model = models.resnet50(weights=None)  # Don't load pretrained weights
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        
        # Load state dict with proper device mapping
        model_bytes = io.BytesIO(model_data)
        
        # Determine device - try to use same device as available
        device = torch.device('cpu')
        if torch.cuda.is_available():
            device = torch.device('cuda')
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device('mps')
        
        print(f"Loading model to device: {device}")
        
        # The state_dict was serialized on the host, possibly on CUDA. Remapping
        # CUDA storages straight to MPS/CUDA via a single-device map_location is
        # unreliable across PyTorch versions and can raise "Attempting to
        # deserialize object on a CUDA device but torch.cuda.is_available() is
        # False". Deserializing to CPU first is universally supported; we then
        # move the in-memory model to the chosen device below.
        state_dict = torch.load(model_bytes, map_location=torch.device('cpu'))
        model.load_state_dict(state_dict)
        model.to(device)
        model.eval()
        
        # Store loaded model
        loaded_model = {'model': model, 'metadata': metadata, 'device': device}
        
        print(f"✓ Model loaded successfully with {num_classes} classes on {device}")
        
        return {
            'status': 'success',
            'message': f'Model loaded successfully with {num_classes} classes',
            'classes': metadata['classes'],
            'device': str(device)
        }
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ Model loading error: {error_detail}")
        raise HTTPException(status_code=400, detail=f'Failed to load model: {str(e)}')

@app.post('/api/infer')
async def infer(req: InferenceRequest):
    """Run inference on normalized image data"""
    global loaded_model
    
    if loaded_model is None:
        raise HTTPException(status_code=400, detail='No model loaded')
    
    try:
        model = loaded_model['model']
        metadata = loaded_model['metadata']
        device = loaded_model.get('device', torch.device('cpu'))
        
        # Convert list to tensor
        image_tensor = torch.tensor(req.image_data, dtype=torch.float32)
        image_tensor = image_tensor.view(1, 3, req.input_size, req.input_size)
        image_tensor = image_tensor.to(device)
        
        # Run inference
        with torch.no_grad():
            output = model(image_tensor)
            probabilities = torch.softmax(output[0], dim=0)
        
        # Get prediction
        predicted_idx = torch.argmax(probabilities).item()
        confidence = probabilities[predicted_idx].item()
        
        # Convert to dict for JSON serialization
        probs_dict = {}
        for i, prob in enumerate(probabilities.cpu().tolist()):
            probs_dict[str(i)] = prob
        
        return {
            'predicted_index': predicted_idx,
            'predicted_class': metadata['classes'][str(predicted_idx)],
            'confidence': float(confidence),
            'probabilities': probs_dict
        }
    except Exception as e:
        import traceback
        print(f"Inference error: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f'Inference failed: {str(e)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run TurboMesh User')
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8001)
    args = parser.parse_args()
    uvicorn.run('main:app', host=args.host, port=args.port, reload=False)

