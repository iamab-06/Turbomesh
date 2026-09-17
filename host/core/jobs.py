import uuid
import os
import hashlib
from fastapi import HTTPException
import time

STORAGE_DIR = 'storage/jobs'

class JobManager:
    def __init__(self):
        self.jobs = {} # job_id -> dict
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)
            
    def create_job(self, client_id: str, operation: str):
        job_id = f'job_{uuid.uuid4().hex}'
        
        job_dir = os.path.join(STORAGE_DIR, job_id)
        os.makedirs(os.path.join(job_dir, 'input'))
        os.makedirs(os.path.join(job_dir, 'output'))
        os.makedirs(os.path.join(job_dir, 'temporary'))
        
        self.jobs[job_id] = {
            'job_id': job_id,
            'client_id': client_id,
            'operation': operation,
            'status': 'CREATED',
            'progress': 0,
            'stage': 'Waiting for files',
            'files': {},
            'created_at': time.time(),
            'result': None
        }
        return self.jobs[job_id]

    def get_job(self, job_id: str, client_id: str):
        job = self.jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail='Job not found')
        if job['client_id'] != client_id:
            raise HTTPException(status_code=403, detail='Forbidden')
        return job

    def save_chunk(self, job_id: str, client_id: str, filename: str, chunk_index: int, chunk_data: bytes):
        job = self.get_job(job_id, client_id)
        if job['status'] not in ['CREATED', 'UPLOADING']:
            raise HTTPException(status_code=400, detail='Job is not accepting uploads')
            
        job['status'] = 'UPLOADING'
        
        temp_dir = os.path.join(STORAGE_DIR, job_id, 'temporary')
        safe_filename = os.path.basename(filename)
        
        chunk_path = os.path.join(temp_dir, f'{safe_filename}.part{chunk_index}')
        with open(chunk_path, 'wb') as f:
            f.write(chunk_data)
            
        return {'status': 'chunk_saved', 'index': chunk_index}

    def finalize_upload(self, job_id: str, client_id: str, filename: str, total_chunks: int, expected_size: int, expected_sha256: str):
        job = self.get_job(job_id, client_id)
        temp_dir = os.path.join(STORAGE_DIR, job_id, 'temporary')
        input_dir = os.path.join(STORAGE_DIR, job_id, 'input')
        safe_filename = os.path.basename(filename)
        
        final_path = os.path.join(input_dir, safe_filename)
        
        hasher = hashlib.sha256()
        actual_size = 0
        
        with open(final_path, 'wb') as outfile:
            for i in range(total_chunks):
                chunk_path = os.path.join(temp_dir, f'{safe_filename}.part{i}')
                if not os.path.exists(chunk_path):
                    os.remove(final_path)
                    raise HTTPException(status_code=400, detail=f'Missing chunk {i}')
                with open(chunk_path, 'rb') as infile:
                    data = infile.read()
                    outfile.write(data)
                    hasher.update(data)
                    actual_size += len(data)
                os.remove(chunk_path) # cleanup
                
        if actual_size != expected_size:
            os.remove(final_path)
            raise HTTPException(status_code=400, detail='Size mismatch')
            
        actual_sha256 = hasher.hexdigest()
        if actual_sha256 != expected_sha256:
            os.remove(final_path)
            raise HTTPException(status_code=400, detail='Checksum mismatch')
            
        job['files'][safe_filename] = {'path': final_path, 'size': actual_size, 'sha256': actual_sha256}
        
        return {'status': 'UPLOAD_COMPLETE', 'file': safe_filename}

job_manager = JobManager()

