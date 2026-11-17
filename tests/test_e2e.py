import time
import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../host')))
from main import app as host_app
from core.auth import auth_manager
import hashlib
import asyncio
from core.jobs import job_manager

client = TestClient(host_app)


def reset_auth_state():
    auth_manager.__init__()


def test_pairing_flow():
    reset_auth_state()
    code = auth_manager.get_pairing_code()
    assert code is not None

    payload = {'pairing_code': code, 'client_id': 'test_client', 'device_name': 'Test', 'os': 'Linux', 'app_version': '1'}
    res = client.post('/api/auth/pair', json=payload)
    assert res.status_code == 200
    assert res.json()['status'] == 'pending'

    res = client.post('/api/clients/test_client/approve')
    assert res.status_code == 200

    res = client.get('/api/auth/status?client_id=test_client')
    assert res.status_code == 200
    assert res.json()['status'] == 'approved'
    assert 'token' in res.json()

    token = res.json()['token']

    # test auth fail
    res = client.post('/api/jobs', json={'operation': 'object_detection'})
    assert res.status_code == 401

    # test auth success
    res = client.post('/api/jobs', json={'operation': 'object_detection'}, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    assert 'job_id' in res.json()


def test_multiple_devices_can_pair_with_same_code():
    reset_auth_state()
    code = auth_manager.get_pairing_code()

    first = {'pairing_code': code, 'client_id': 'device_a', 'device_name': 'A', 'os': 'Linux', 'app_version': '1'}
    second = {'pairing_code': code, 'client_id': 'device_b', 'device_name': 'B', 'os': 'Linux', 'app_version': '1'}

    first_res = client.post('/api/auth/pair', json=first)
    second_res = client.post('/api/auth/pair', json=second)
    assert first_res.status_code == 200
    assert second_res.status_code == 200

    assert client.post('/api/clients/device_a/approve').status_code == 200
    assert client.post('/api/clients/device_b/approve').status_code == 200

    assert client.get('/api/auth/status?client_id=device_a').json()['status'] == 'approved'
    assert client.get('/api/auth/status?client_id=device_b').json()['status'] == 'approved'


def test_pairing_code_refreshes_after_5_minutes():
    reset_auth_state()
    old_code = auth_manager.get_pairing_code()
    auth_manager.pairing_code = '000000'
    auth_manager.pairing_code_expiry = time.time() - 301

    refreshed = auth_manager.get_pairing_code()
    assert refreshed != '000000'
    assert refreshed != old_code


def test_hand_sign_recognition_job_creation():
    """Test that hand_sign_recognition job can be created and processed."""
    reset_auth_state()
    code = auth_manager.get_pairing_code()

    # Pair and approve
    payload = {'pairing_code': code, 'client_id': 'test_client_hs', 'device_name': 'Test', 'os': 'Linux', 'app_version': '1'}
    client.post('/api/auth/pair', json=payload)
    client.post('/api/clients/test_client_hs/approve')
    
    token = client.get('/api/auth/status?client_id=test_client_hs').json()['token']

    # Create hand_sign_recognition job
    res = client.post('/api/jobs', json={'operation': 'hand_sign_recognition'}, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    job = res.json()
    assert job['operation'] == 'hand_sign_recognition'
    assert job['status'] == 'CREATED'
    assert 'job_id' in job
    
    # Verify job can be retrieved
    res = client.get(f'/api/jobs/{job["job_id"]}', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    assert res.json()['operation'] == 'hand_sign_recognition'


def test_hand_sign_recognition_file_upload():
    """Test uploading a dataset ZIP for hand sign recognition."""
    reset_auth_state()
    code = auth_manager.get_pairing_code()

    # Pair and approve
    payload = {'pairing_code': code, 'client_id': 'test_client_hs2', 'device_name': 'Test', 'os': 'Linux', 'app_version': '1'}
    client.post('/api/auth/pair', json=payload)
    client.post('/api/clients/test_client_hs2/approve')
    
    token = client.get('/api/auth/status?client_id=test_client_hs2').json()['token']

    # Create hand_sign_recognition job
    res = client.post('/api/jobs', json={'operation': 'hand_sign_recognition'}, headers={'Authorization': f'Bearer {token}'})
    job_id = res.json()['job_id']

    # Load test dataset
    zip_path = 'tests/test_hand_sign_dataset.zip'
    assert os.path.exists(zip_path), f"Test dataset not found at {zip_path}"
    
    with open(zip_path, 'rb') as f:
        zip_data = f.read()
    
    # Calculate SHA256
    sha256 = hashlib.sha256(zip_data).hexdigest()
    
    # Upload as single chunk
    files = {'file': ('test_dataset.zip', zip_data, 'application/zip')}
    data = {'chunk_index': '0', 'filename': 'test_dataset.zip'}
    
    res = client.post(
        f'/api/jobs/{job_id}/upload/chunk',
        data=data,
        files=files,
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 200
    
    # Finalize upload
    finalize_payload = {
        'filename': 'test_dataset.zip',
        'total_chunks': 1,
        'expected_size': len(zip_data),
        'expected_sha256': sha256
    }
    res = client.post(
        f'/api/jobs/{job_id}/upload/finalize',
        json=finalize_payload,
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 200
    
    # Verify job is marked as UPLOAD_COMPLETE or COMPLETED (if it finished quickly)
    res = client.get(f'/api/jobs/{job_id}', headers={'Authorization': f'Bearer {token}'})
    job = res.json()
    assert job['status'] in ['UPLOAD_COMPLETE', 'COMPLETED', 'PROCESSING']
    
    # If completed, verify result files were generated
    if job['status'] == 'COMPLETED':
        assert 'result_files' in job
        assert 'hand_sign_model.pt' in job['result_files']
        assert 'hand_sign_metadata.json' in job['result_files']



