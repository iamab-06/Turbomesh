#!/usr/bin/env python3
"""
Connection diagnostic tool for TurboMesh
Tests connectivity between user and host apps
"""
import asyncio
import httpx
import sys

async def test_connection(host_ip="127.0.0.1", host_port=8000, user_port=9001):
    """Test connection between user and host"""
    
    print("="*60)
    print("TurboMesh Connection Diagnostic Tool")
    print("="*60)
    print()
    
    results = {
        'host_reachable': False,
        'user_reachable': False,
        'host_info': None,
        'pairing_possible': False
    }
    
    # Test 1: Host reachability
    print(f"[1/4] Testing Host at http://{host_ip}:{host_port}")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://{host_ip}:{host_port}/api/host/info")
            if response.status_code == 200:
                results['host_reachable'] = True
                results['host_info'] = response.json()
                print(f"      ✓ Host is reachable")
                print(f"      Host IP: {results['host_info'].get('ip')}")
            else:
                print(f"      ✗ Host returned status {response.status_code}")
    except httpx.ConnectError:
        print(f"      ✗ Cannot connect to host")
        print(f"        Make sure host is running: cd host && python main.py --port {host_port}")
    except Exception as e:
        print(f"      ✗ Error: {str(e)}")
    
    print()
    
    # Test 2: User reachability
    print(f"[2/4] Testing User at http://127.0.0.1:{user_port}")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://127.0.0.1:{user_port}/api/status")
            if response.status_code == 200:
                results['user_reachable'] = True
                data = response.json()
                print(f"      ✓ User is reachable")
                print(f"      Client ID: {data.get('client_id')}")
            else:
                print(f"      ✗ User returned status {response.status_code}")
    except httpx.ConnectError:
        print(f"      ✗ Cannot connect to user")
        print(f"        Make sure user is running: cd user && python main.py --port {user_port}")
    except Exception as e:
        print(f"      ✗ Error: {str(e)}")
    
    print()
    
    # Test 3: CORS check
    print(f"[3/4] Testing CORS configuration")
    if results['host_reachable']:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.options(
                    f"http://{host_ip}:{host_port}/api/auth/pair",
                    headers={
                        'Origin': f'http://localhost:{user_port}',
                        'Access-Control-Request-Method': 'POST'
                    }
                )
                if response.status_code in [200, 204]:
                    print(f"      ✓ CORS is configured")
                else:
                    print(f"      ⚠ CORS may not be configured properly")
        except Exception as e:
            print(f"      ⚠ Could not test CORS: {str(e)}")
    else:
        print(f"      ⚠ Skipping (host not reachable)")
    
    print()
    
    # Test 4: Pairing test
    print(f"[4/4] Testing pairing endpoint")
    if results['host_reachable']:
        try:
            # Try with an invalid code to test endpoint
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"http://{host_ip}:{host_port}/api/auth/pair",
                    json={
                        'pairing_code': '000000',
                        'client_id': 'test_client',
                        'device_name': 'test',
                        'os': 'test',
                        'app_version': '1.0.0'
                    }
                )
                # We expect 400 for invalid code, but endpoint should respond
                if response.status_code == 400:
                    error = response.json()
                    if 'expired' in error.get('detail', '').lower() or 'invalid' in error.get('detail', '').lower():
                        results['pairing_possible'] = True
                        print(f"      ✓ Pairing endpoint is working")
                        print(f"        (Got expected error for test code)")
                    else:
                        print(f"      ⚠ Endpoint responded but with unexpected error")
                        print(f"        {error.get('detail')}")
                elif response.status_code == 200:
                    print(f"      ⚠ Test code was accepted (unexpected)")
                else:
                    print(f"      ⚠ Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"      ✗ Error testing pairing: {str(e)}")
    else:
        print(f"      ⚠ Skipping (host not reachable)")
    
    print()
    print("="*60)
    print("Summary")
    print("="*60)
    print()
    
    if results['host_reachable'] and results['user_reachable'] and results['pairing_possible']:
        print("✓ All tests passed!")
        print()
        print("You can now pair the user with the host:")
        print(f"  1. Open host at http://{host_ip}:{host_port}")
        print(f"  2. Note the pairing code")
        print(f"  3. Open user at http://127.0.0.1:{user_port}")
        print(f"  4. Enter host IP: {host_ip}, port: {host_port}, and the pairing code")
        print(f"  5. Click CONNECT TO HOST")
        print(f"  6. Approve the request on host dashboard")
        return 0
    else:
        print("✗ Some tests failed. Issues found:")
        print()
        if not results['host_reachable']:
            print("  - Host is not reachable")
            print(f"    Fix: cd host && python main.py --port {host_port}")
        if not results['user_reachable']:
            print("  - User is not reachable")
            print(f"    Fix: cd user && python main.py --port {user_port}")
        if results['host_reachable'] and not results['pairing_possible']:
            print("  - Pairing endpoint has issues")
            print(f"    Fix: Check host logs for errors")
        return 1

async def main():
    if len(sys.argv) > 1:
        host_ip = sys.argv[1]
    else:
        host_ip = "127.0.0.1"
    
    if len(sys.argv) > 2:
        host_port = int(sys.argv[2])
    else:
        host_port = 8000
    
    if len(sys.argv) > 3:
        user_port = int(sys.argv[3])
    else:
        user_port = 9001
    
    exit_code = await test_connection(host_ip, host_port, user_port)
    sys.exit(exit_code)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
