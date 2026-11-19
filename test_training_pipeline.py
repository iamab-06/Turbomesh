"""
Test the complete hand-sign training pipeline with archive.zip.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'host'))

import shutil
import zipfile
from core.hand_sign_landmark_training import extract_and_validate_dataset, train_landmark_model

print("=" * 80)
print("TESTING COMPLETE TRAINING PIPELINE WITH ARCHIVE.ZIP")
print("=" * 80)

# Setup paths
zip_path = 'archive.zip'
test_dir = 'test_training_run'
input_dir = os.path.join(test_dir, 'input')
output_dir = os.path.join(test_dir, 'output')
extract_dir = os.path.join(input_dir, 'extracted_dataset')

# Clean up any previous test
if os.path.exists(test_dir):
    shutil.rmtree(test_dir)

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
os.makedirs(extract_dir, exist_ok=True)

# Copy zip to input
print("\n[1/5] Copying dataset...")
shutil.copy(zip_path, os.path.join(input_dir, 'archive.zip'))
print("[OK] Dataset copied")

# Extract and validate
print("\n[2/5] Extracting and validating dataset...")
try:
    dataset_dir = extract_and_validate_dataset(
        os.path.join(input_dir, 'archive.zip'),
        extract_dir
    )
    print(f"[OK] Dataset validated at: {dataset_dir}")
except Exception as e:
    print(f"[ERROR] Validation failed: {e}")
    sys.exit(1)

# Check what's in dataset_dir
print("\n[3/5] Checking dataset structure...")
classes = [d for d in os.listdir(dataset_dir) 
           if os.path.isdir(os.path.join(dataset_dir, d)) and not d.startswith('.')]
print(f"[OK] Found {len(classes)} classes: {sorted(classes)}")

total_images = 0
for cls in classes:
    cls_path = os.path.join(dataset_dir, cls)
    images = [f for f in os.listdir(cls_path) 
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    total_images += len(images)
    print(f"  Class {cls}: {len(images)} images")

print(f"[OK] Total images: {total_images}")

# Create mock job object
job = {
    'stage': 'Starting',
    'progress': 0
}

# Train model
print("\n[4/5] Training model with MediaPipe landmarks...")
print("(This may take a few minutes...)")
try:
    result_files = train_landmark_model(dataset_dir, job, output_dir)
    print(f"\n[OK] Training complete!")
    print(f"  Generated files: {result_files}")
except Exception as e:
    print(f"\n[ERROR] Training failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check results
print("\n[5/5] Verifying results...")
import json

metadata_path = os.path.join(output_dir, 'hand_sign_metadata.json')
if os.path.exists(metadata_path):
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    print("\n--- Training Results ---")
    print(f"Model: {metadata['model_name']}")
    print(f"Version: {metadata['model_version']}")
    print(f"Classes: {metadata['num_classes']}")
    print(f"Feature dimensions: {metadata['feature_extraction']['total_features']}")
    
    training = metadata['training']
    print(f"\nDataset:")
    print(f"  Total samples: {training['dataset_size']}")
    print(f"  Train: {training['train_size']}")
    print(f"  Validation: {training['val_size']}")
    print(f"  Failed images: {training['failed_images']}")
    
    metrics = metadata['metrics']
    print(f"\nMetrics:")
    print(f"  Training accuracy: {metrics['training_accuracy']:.2%}")
    print(f"  Validation accuracy: {metrics['validation_accuracy']:.2%}")
    
    # Check if actual landmarks were used
    feature_method = metadata['feature_extraction']['method']
    print(f"\nFeature extraction: {feature_method}")
    
    if training['failed_images'] == training['dataset_size']:
        print("\n[WARNING] ALL images failed landmark extraction!")
        print("   Model was trained on FALLBACK features (color/texture)")
        print("   This is NOT landmark-based hand-sign recognition!")
    elif training['failed_images'] > training['dataset_size'] * 0.5:
        print(f"\n[WARNING] {training['failed_images']} / {training['dataset_size'] + training['failed_images']} images failed")
        print(f"   Success rate: {100 * training['dataset_size'] / (training['dataset_size'] + training['failed_images']):.1f}%")
    else:
        success_count = training['dataset_size']
        total_attempted = training['dataset_size'] + training['failed_images']
        success_rate = 100 * success_count / total_attempted
        print(f"\n[SUCCESS] {success_count} / {total_attempted} images extracted")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Validation accuracy: {metrics['validation_accuracy']:.1%}")
    
else:
    print("[ERROR] Metadata file not found!")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

# Cleanup (disabled for inspection)
print("\nTest directory preserved for inspection:", test_dir)
# shutil.rmtree(test_dir)
# print("✓ Cleanup complete")
