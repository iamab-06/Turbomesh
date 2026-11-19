import pytest
import time
from fastapi.testclient import TestClient
from host.main import app
from host.core.rate_limiter import pairing_rate_limiter

client = TestClient(app)

def setup_function():
    # Reset limiter history before test
    pairing_rate_limiter.reset()

def test_rate_limiter_allows_up_to_limit():
    payload = {
        "pairing_code": "000000",
        "client_id": "test_client_1",
        "device_name": "TestDevice",
        "os": "Windows",
        "app_version": "1.0.0"
    }

    # First 5 requests should pass the rate limiter (return 200 or 400 depending on code validity, not 429)
    for i in range(5):
        res = client.post("/api/auth/pair", json=payload)
        assert res.status_code != 429, f"Request {i+1} was unexpectedly rate limited"
        print(f"Request {i+1} status: {res.status_code} (Passed Rate Limiter)")

    # 6th request MUST be blocked with 429
    res = client.post("/api/auth/pair", json=payload)
    assert res.status_code == 429, f"Request 6 should have been 429, got {res.status_code}"
    data = res.json()
    assert "Rate limit exceeded" in data["detail"]
    assert "Retry-After" in res.headers
    print(f"Request 6 status: {res.status_code} - Blocked as expected: {data['detail']}")

def test_rate_limiter_distinct_ips():
    payload = {
        "pairing_code": "000000",
        "client_id": "test_client_2",
        "device_name": "TestDevice",
        "os": "Windows",
        "app_version": "1.0.0"
    }

    # Simulate IP 1 making 5 requests
    for _ in range(5):
        pairing_rate_limiter.check("192.168.1.101")
    
    allowed_ip1, _, _ = pairing_rate_limiter.check("192.168.1.101")
    assert allowed_ip1 is False, "IP 1 should be blocked"

    # IP 2 should NOT be blocked
    allowed_ip2, _, remaining = pairing_rate_limiter.check("192.168.1.102")
    assert allowed_ip2 is True, "IP 2 should be allowed"
    assert remaining == 4
    print("Distinct IP test passed successfully!")

if __name__ == "__main__":
    test_rate_limiter_allows_up_to_limit()
    pairing_rate_limiter.reset()
    test_rate_limiter_distinct_ips()
    print("ALL RATE LIMITER TESTS PASSED!")
