"""
Analyze archive.zip dataset for MediaPipe compatibility.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'host'))

import zipfile
from PIL import Image
import io
from core.hand_landmarks import extract_hand_landmarks, get_hand_features
import numpy as np

zip_path = 'archive.zip'

print("=" * 80)
print("ANALYZING ARCHIVE.ZIP DATASET")
print("=" * 80)

with zipfile.ZipFile(zip_path, 'r') as zf:
    all_files = zf.namelist()
    
    # Find structure
    print(f"\nTotal files in ZIP: {len(all_files)}")
    
    # Get image files
    image_files = [f for f in all_files 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')) 
                   and not f.startswith('__MACOSX')
                   and not f.startswith('.')]
    
    print(f"Image files found: {len(image_files)}")
    
    if not image_files:
        print("\n❌ No image files found in archive!")
        sys.exit(1)
    
    # Analyze directory structure
    print("\n--- Directory Structure ---")
    dirs = set()
    for f in image_files:
        parts = f.split('/')
        if len(parts) > 1:
            dirs.add(parts[0] if len(parts) == 2 else '/'.join(parts[:-1]))
    
    print(f"Found {len(dirs)} directories/classes:")
    for d in sorted(dirs)[:20]:
        count = len([f for f in image_files if f.startswith(d + '/')])
        print(f"  - {d}: {count} images")
    
    if len(dirs) > 20:
        print(f"  ... and {len(dirs) - 20} more")
    
    # Sample and analyze images
    print("\n--- Image Analysis (First 5 samples) ---")
    
    success_count = 0
    failure_count = 0
    
    for idx, img_file in enumerate(image_files[:10]):
        print(f"\n[Sample {idx + 1}] {img_file}")
        
        try:
            img_data = zf.read(img_file)
            img = Image.open(io.BytesIO(img_data))
            
            print(f"  Size: {img.size}, Mode: {img.mode}")
            
            # Convert to array
            arr = np.array(img.convert('RGB'))
            
            # Check image characteristics
            print(f"  Pixel range: [{arr.min()}, {arr.max()}], Mean: {arr.mean():.1f}")
            
            # Check if visualization (white background + red dots)
            white_pixels = np.sum((arr > 200).all(axis=2))
            total_pixels = arr.shape[0] * arr.shape[1]
            white_ratio = white_pixels / total_pixels
            
            red_channel = arr[:, :, 0]
            green_channel = arr[:, :, 1]
            blue_channel = arr[:, :, 2]
            red_pixels = np.sum((red_channel > 200) & (green_channel < 100) & (blue_channel < 100))
            red_ratio = red_pixels / total_pixels
            
            print(f"  White background: {white_ratio:.1%}, Red dots: {red_ratio:.1%}")
            
            if white_ratio > 0.5:
                print(f"  ⚠️  Likely a visualization image (white background)")
            
            # Try MediaPipe extraction
            landmarks = extract_hand_landmarks(img)
            
            if landmarks is not None:
                print(f"  ✅ LANDMARKS DETECTED: {landmarks.shape}")
                print(f"     Wrist: {landmarks[0]}")
                print(f"     Thumb tip: {landmarks[4]}")
                success_count += 1
            else:
                print(f"  ❌ No hand detected by MediaPipe")
                failure_count += 1
            
            # Try full feature extraction
            features = get_hand_features(img, include_geometric=True)
            if features is not None:
                print(f"  ✅ Features extracted: {len(features)} dimensions")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failure_count += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total images in dataset: {len(image_files)}")
    print(f"Classes detected: {len(dirs)}")
    print(f"Sample test results (first 10 images):")
    print(f"  ✅ Successful landmark extraction: {success_count}")
    print(f"  ❌ Failed landmark extraction: {failure_count}")
    
    if success_count > 0:
        success_rate = success_count / (success_count + failure_count) * 100
        print(f"\n✅ SUCCESS RATE: {success_rate:.1f}%")
        print(f"\n🎉 This dataset appears COMPATIBLE with MediaPipe landmark extraction!")
        print(f"   Expected to extract landmarks from approximately {success_rate:.0f}% of images.")
    else:
        print(f"\n❌ INCOMPATIBLE DATASET")
        print(f"   MediaPipe could not detect hands in any test images.")
        print(f"   This dataset likely contains visualization images, not photographs.")
    
    print("=" * 80)
