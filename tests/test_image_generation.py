import os
import sys
import time
import json
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../host')))
from main import app as host_app
from core.auth import auth_manager
from core.jobs import job_manager, STORAGE_DIR
from core.image_generation import parse_prompt, generate_image_tensor, run_image_generation

client = TestClient(host_app)


def reset_auth():
    auth_manager.__init__()


def test_parse_prompt_cyberpunk():
    result = parse_prompt("A futuristic cyberpunk city with neon lights and flying cars")
    assert result['style'] == 'cyberpunk'
    assert result['is_neon'] is True
    assert 'city' in result['subjects']


def test_parse_prompt_space():
    result = parse_prompt("Deep space nebula with glowing stars and colorful planets")
    assert result['style'] == 'space'
    assert 'stars' in result['subjects']


def test_parse_prompt_style_override():
    result = parse_prompt("Mystic castle on a mountain", user_style="fantasy")
    assert result['style'] == 'fantasy'
    assert 'mountains' in result['subjects']


def test_generate_image_tensor_dimensions_and_metadata():
    img_bgr, meta = generate_image_tensor(
        prompt="Golden sunset over ocean waves",
        width=256,
        height=256,
        seed=123,
        style_override="sunset"
    )
    assert img_bgr.shape == (256, 256, 3)
    assert img_bgr.dtype == 'uint8'
    assert meta['operation'] == 'image_generation'
    assert meta['seed'] == 123
    assert meta['width'] == 256
    assert meta['height'] == 256
    assert meta['style'] == 'sunset'
    assert 'generation_time_seconds' in meta


def test_run_image_generation_worker():
    tmp_out = os.path.join(STORAGE_DIR, 'test_gen_worker_output')
    os.makedirs(tmp_out, exist_ok=True)
    
    job = {
        'prompt': 'Futuristic neon vehicle on cyber highway',
        'params': {'width': 256, 'height': 256, 'seed': 99, 'style': 'synthwave'}
    }
    
    result_files = run_image_generation(job, None, tmp_out)
    assert 'generated_image.png' in result_files
    assert 'generation_metadata.json' in result_files
    
    # Check that image was written and has non-zero size
    img_path = os.path.join(tmp_out, 'generated_image.png')
    assert os.path.exists(img_path)
    assert os.path.getsize(img_path) > 1000
    
    # Check that metadata was written and contains valid json
    meta_path = os.path.join(tmp_out, 'generation_metadata.json')
    assert os.path.exists(meta_path)
    with open(meta_path, 'r') as f:
        meta_data = json.load(f)
    assert meta_data['prompt'] == 'Futuristic neon vehicle on cyber highway'
    assert meta_data['style'] == 'synthwave'


def test_host_image_generation_end_to_end():
    reset_auth()
    code = auth_manager.get_pairing_code()
    
    # Pair and approve client
    pair_res = client.post('/api/auth/pair', json={
        'pairing_code': code,
        'client_id': 'gen_client_1',
        'device_name': 'TestDevice',
        'os': 'Windows',
        'app_version': '1.0.0'
    })
    assert pair_res.status_code == 200
    
    appr_res = client.post('/api/clients/gen_client_1/approve')
    assert appr_res.status_code == 200
    
    token = client.get('/api/auth/status?client_id=gen_client_1').json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create image generation job
    create_res = client.post('/api/jobs', json={
        'operation': 'image_generation',
        'prompt': 'A cyberpunk neon skyscraper under starry night sky',
        'params': {'width': 256, 'height': 256, 'seed': 42, 'style': 'cyberpunk'}
    }, headers=headers)
    
    assert create_res.status_code == 200
    job_data = create_res.json()
    job_id = job_data['job_id']
    assert job_data['operation'] == 'image_generation'
    assert job_data['status'] in ['PENDING', 'PROCESSING', 'COMPLETED']
    
    # Poll for completion
    max_retries = 40
    completed = False
    for _ in range(max_retries):
        poll_res = client.get(f'/api/jobs/{job_id}', headers=headers)
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data['status'] == 'COMPLETED':
            completed = True
            break
        time.sleep(0.5)
        
    assert completed, f"Job did not complete in time, status: {poll_data.get('status')}"
    assert 'generated_image.png' in poll_data['result_files']
    assert 'generation_metadata.json' in poll_data['result_files']
    
    # Download generated image
    img_res = client.get(f'/api/jobs/{job_id}/result/generated_image.png', headers=headers)
    assert img_res.status_code == 200
    assert len(img_res.content) > 1000
    assert img_res.headers['content-type'].startswith('image/')
    
    # Download metadata
    meta_res = client.get(f'/api/jobs/{job_id}/result/generation_metadata.json', headers=headers)
    assert meta_res.status_code == 200
    meta_json = meta_res.json()
    assert meta_json['operation'] == 'image_generation'
    assert meta_json['prompt'] == 'A cyberpunk neon skyscraper under starry night sky'
    assert meta_json['style'] == 'cyberpunk'


def test_run_image_generation_with_sd_params():
    tmp_out = os.path.join(STORAGE_DIR, 'test_gen_sd_output')
    os.makedirs(tmp_out, exist_ok=True)
    
    job = {
        'prompt': 'Cinematic cyberpunk skyline, highly detailed, 8k',
        'params': {
            'engine': 'stable-diffusion',
            'model_id': 'stabilityai/sd-turbo',
            'width': 256,
            'height': 256,
            'seed': 42
        }
    }
    
    result_files = run_image_generation(job, None, tmp_out)
    assert 'generated_image.png' in result_files
    assert 'generation_metadata.json' in result_files
    
    img_path = os.path.join(tmp_out, 'generated_image.png')
    assert os.path.exists(img_path)
    assert os.path.getsize(img_path) > 1000
    
    meta_path = os.path.join(tmp_out, 'generation_metadata.json')
    assert os.path.exists(meta_path)
    with open(meta_path, 'r') as f:
        meta_data = json.load(f)
    assert meta_data['prompt'] == 'Cinematic cyberpunk skyline, highly detailed, 8k'
