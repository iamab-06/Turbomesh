import time
import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../host')))
from main import app as host_app
from core.auth import auth_manager

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

