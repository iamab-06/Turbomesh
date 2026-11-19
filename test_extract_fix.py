import sys, os
sys.path.insert(0, 'host')

from core.hand_sign_landmark_training import extract_and_validate_dataset
import shutil

extract_dir = 'test_extract'
if os.path.exists(extract_dir):
    shutil.rmtree(extract_dir)
os.makedirs(extract_dir)

try:
    dataset_dir = extract_and_validate_dataset('archive.zip', extract_dir)
    print(f"Dataset found at: {dataset_dir}")
    
    # List classes
    classes = sorted([d for d in os.listdir(dataset_dir) 
                      if os.path.isdir(os.path.join(dataset_dir, d)) and not d.startswith('.')])
    print(f"Classes: {classes}")
    
    # Count images
    for cls in classes[:5]:
        cls_path = os.path.join(dataset_dir, cls)
        images = [f for f in os.listdir(cls_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"  Class {cls}: {len(images)} images")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
