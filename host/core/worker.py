import asyncio
import traceback
from core.jobs import job_manager, STORAGE_DIR
from core.processing import run_object_detection, run_image_similarity
import os

async def process_job(job_id: str):
    job = job_manager.jobs.get(job_id)
    if not job: return
    
    job['status'] = 'PROCESSING'
    job['progress'] = 10
    job['stage'] = 'Starting inference'
    
    input_dir = os.path.join(STORAGE_DIR, job_id, 'input')
    output_dir = os.path.join(STORAGE_DIR, job_id, 'output')
    
    try:
        if job['operation'] == 'object_detection':
            job['stage'] = 'Running YOLO object detection'
            result_files = await asyncio.to_thread(run_object_detection, job, input_dir, output_dir)
        elif job['operation'] == 'image_similarity':
            job['stage'] = 'Extracting features and computing similarity'
            result_files = await asyncio.to_thread(run_image_similarity, job, input_dir, output_dir)
        else:
            raise Exception('Unknown operation')
            
        job['progress'] = 100
        job['status'] = 'COMPLETED'
        job['stage'] = 'Finished'
        job['result_files'] = result_files
    except Exception as e:
        job['status'] = 'FAILED'
        job['stage'] = f'Error: {str(e)}'
        print(f'Job {job_id} failed: {traceback.format_exc()}')

