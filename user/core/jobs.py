import httpx
import os
import hashlib
import asyncio
from .client import tm_client

CHUNK_SIZE = 1024 * 1024 # 1MB

class JobManager:
    async def create_job(self, operation: str):
        if not tm_client.token:
            raise Exception('Not authenticated')
        
        headers = {'Authorization': f'Bearer {tm_client.token}'}
        async with httpx.AsyncClient() as client:
            res = await client.post(f'{tm_client.host_url}/api/jobs', json={'operation': operation}, headers=headers)
            res.raise_for_status()
            return res.json()

    async def upload_file(self, job_id: str, filepath: str, progress_callback=None):
        if not tm_client.token:
            raise Exception('Not authenticated')
            
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        total_chunks = (filesize + CHUNK_SIZE - 1) // CHUNK_SIZE
        
        headers = {'Authorization': f'Bearer {tm_client.token}'}
        
        hasher = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            for i in range(total_chunks):
                chunk_data = f.read(CHUNK_SIZE)
                hasher.update(chunk_data)
                
                # Retry logic
                for attempt in range(3):
                    try:
                        async with httpx.AsyncClient() as client:
                            files = {'file': (filename, chunk_data, 'application/octet-stream')}
                            data = {'chunk_index': str(i), 'filename': filename}
                            res = await client.post(f'{tm_client.host_url}/api/jobs/{job_id}/upload/chunk', data=data, files=files, headers=headers)
                            res.raise_for_status()
                            break
                    except Exception as e:
                        if attempt == 2:
                            raise Exception(f'Failed to upload chunk {i}: {e}')
                        await asyncio.sleep(1)
                        
                if progress_callback:
                    progress_callback(i + 1, total_chunks)

        # Finalize
        payload = {
            'filename': filename,
            'total_chunks': total_chunks,
            'expected_size': filesize,
            'expected_sha256': hasher.hexdigest()
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(f'{tm_client.host_url}/api/jobs/{job_id}/upload/finalize', json=payload, headers=headers)
            res.raise_for_status()
            return res.json()

user_job_manager = JobManager()

