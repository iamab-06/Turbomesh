"""Simple training test with better error handling."""
import sys, os
sys.path.insert(0, 'host')

import zipfile, shutil
from core.hand_sign_landmark_training import LandmarkDataset

# Extract archive.zip
extract_dir = 'simple_test_extract'
if os.path.exists(extract_dir):
    shutil.rmtree(extract_dir)
os.makedirs(extract_dir)

print("Extracting...")
with zipfile.ZipFile('archive.zip', 'r') as zf:
    zf.extractall(extract_dir)

dataset_dir = os.path.join(extract_dir, 'ASL Digits', 'asl_dataset_digits')
print(f"Dataset directory: {dataset_dir}")
print(f"Exists: {os.path.exists(dataset_dir)}")

try:
    print("\nLoading dataset and extracting landmarks...")
    dataset = LandmarkDataset(dataset_dir)
    
    print(f"\nDataset loaded:")
    print(f"  Total samples extracted: {len(dataset.features)}")
    print(f"  Failed images: {len(dataset.failed_images)}")
    
    if len(dataset.features) > 0:
        print(f"  Feature dimensions: {len(dataset.features[0])}")
        print(f"\n✅ SUCCESS! Landmarks extracted from {len(dataset.features)} images")
        
        X, y = dataset.get_data()
        print(f"\nFinal dataset shape: X={X.shape}, y={y.shape}")
        
        # Show some failed images
        if dataset.failed_images:
            print(f"\nFailed images (first 5):")
            for cls, img, reason in dataset.failed_images[:5]:
                print(f"  - {cls}/{img}: {reason}")
    else:
        print("\n❌ FAILURE: No landmarks extracted!")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\nCleaning up...")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    print("Done.")
