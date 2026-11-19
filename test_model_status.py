#!/usr/bin/env python3
"""
Test script to verify the model status endpoint works correctly
"""
import sys
import asyncio
sys.path.insert(0, 'user')

from main import app, loaded_model
from fastapi.testclient import TestClient

client = TestClient(app)

def test_model_status_not_loaded():
    """Test model status when no model is loaded"""
    response = client.get('/api/model-status')
    assert response.status_code == 200
    
    data = response.json()
    print("Test 1: Model not loaded")
    print(f"  Response: {data}")
    
    assert data['loaded'] == False
    assert data['model_type'] is None
    assert data['num_classes'] == 0
    assert 'No model loaded' in data['message']
    print("  ✓ PASSED\n")

def test_inference_without_model():
    """Test inference endpoint when no model is loaded"""
    response = client.post('/api/infer', json={
        'frame_data': 'fake_base64_data',
        'image_width': 640,
        'image_height': 480
    })
    
    print("Test 2: Inference without model")
    print(f"  Status Code: {response.status_code}")
    
    assert response.status_code == 400
    
    data = response.json()
    print(f"  Error Message: {data['detail']}")
    
    assert 'No model loaded' in data['detail']
    assert 'Please complete a training job' in data['detail']
    print("  ✓ PASSED\n")

if __name__ == '__main__':
    print("="*60)
    print("Testing Model Status Endpoint")
    print("="*60 + "\n")
    
    try:
        test_model_status_not_loaded()
        test_inference_without_model()
        
        print("="*60)
        print("All tests passed! ✓")
        print("="*60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
