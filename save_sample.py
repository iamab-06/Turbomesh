"""Save sample images for visual inspection."""
import zipfile
from PIL import Image
import io

zip_path = 'host/storage/jobs/job_2969c50bc1c44e7a9cab8ff8227c71ac/input/0to9.zip'
output_dir = 'sample_images'

import os
os.makedirs(output_dir, exist_ok=True)

with zipfile.ZipFile(zip_path, 'r') as zf:
    jpg_files = [f for f in zf.namelist() if f.endswith('.jpg') and not f.startswith('__MACOSX')]
    
    # Save first 3 images
    for i, img_file in enumerate(jpg_files[:3]):
        img_data = zf.read(img_file)
        img = Image.open(io.BytesIO(img_data))
        
        # Get class from path
        class_num = img_file.split('/')[1]
        output_path = os.path.join(output_dir, f'sample_class_{class_num}_{i}.jpg')
        img.save(output_path)
        print(f"Saved: {output_path}")

print(f"\nSaved {min(3, len(jpg_files))} sample images to {output_dir}/")
