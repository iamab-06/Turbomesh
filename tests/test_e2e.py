import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../host')))
from main import app as host_app
from core.auth import auth_manager

client = TestClient(host_app)

def test_pairing_flow():
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
    assert res.status_code == 403
    
    # test auth success
    res = client.post('/api/jobs', json={'operation': 'object_detection'}, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    assert 'job_id' in res.json()

