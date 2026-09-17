import httpx
import uuid
import platform
import asyncio

class TurboMeshClient:
    def __init__(self):
        self.client_id = f'client_{uuid.uuid4().hex[:8]}'
        self.device_name = platform.node()
        self.os_name = platform.system()
        self.app_version = '1.0.0'
        
        self.host_url = None
        self.token = None
        
    async def request_pairing(self, host_ip: str, port: int, pairing_code: str):
        self.host_url = f'http://{host_ip}:{port}'
        
        payload = {
            'pairing_code': pairing_code,
            'client_id': self.client_id,
            'device_name': self.device_name,
            'os': self.os_name,
            'app_version': self.app_version
        }
        
        async with httpx.AsyncClient() as client:
            res = await client.post(f'{self.host_url}/api/auth/pair', json=payload)
            res.raise_for_status()
            return res.json()
            
    async def check_status(self):
        if not self.host_url:
            return {'status': 'disconnected'}
            
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f'{self.host_url}/api/auth/status?client_id={self.client_id}')
                if res.status_code == 200:
                    data = res.json()
                    if data.get('status') == 'approved':
                        self.token = data.get('token')
                    return data
                return {'status': 'error', 'code': res.status_code}
            except Exception as e:
                return {'status': 'error', 'detail': str(e)}
                
    async def get_host_info(self):
        if not self.host_url:
            return None
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f'{self.host_url}/api/host/info')
                if res.status_code == 200:
                    return res.json()
            except Exception:
                pass
        return None

tm_client = TurboMeshClient()

