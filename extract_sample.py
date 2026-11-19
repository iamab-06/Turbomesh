"""
Extract and examine sample images from the dataset.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'host'))

import zipfile
from PIL import Image
import io
from core.hand_landmarks import extract_hand_landmarks, get_hand_features
import numpy as np

zip_path = 'host/storage/jobs/job_2969c50bc1c44e7a9cab8ff8227c71ac/input/0to9.zip'

print("Extracting and analyzing sample images from dataset...")
print("=" * 80)

with zipfile.ZipFile(zip_path, 'r') as zf:
    # Get all jpg files
    jpg_files = [f for f in zf.namelist() if f.endswith('.jpg') and not f.startswith('__MACOSX')]
    
    print(f"Total images in dataset: {len(jpg_files)}\n")
    
    # Sample 3 images from different classes
    samples = []
    for i in range(10):
        class_images = [f for f in jpg_files if f'/{i}/' in f]
        if class_images:
            samples.append(class_images[0])
    
    # Analyze first 5 samples
    for idx, img_file in enumerate(samples[:5]):
        print(f"\n--- Image {idx + 1}: {img_file} ---")
        
        # Read image
        img_data = zf.read(img_file)
        img = Image.open(io.BytesIO(img_data))
        
        print(f"  Image size: {img.size}")
        print(f"  Image mode: {img.mode}")
        
        # Convert to numpy to check pixel values
        arr = np.array(img)
        print(f"  Array shape: {arr.shape}")
        print(f"  Min pixel: {arr.min()}, Max pixel: {arr.max()}")
        print(f"  Mean pixel: {arr.mean():.1f}")
        
        # Check if this looks like a visualization (mostly white with red dots)
        if len(arr.shape) == 3:
            # Check red channel dominance at certain pixels
            red_channel = arr[:, :, 0]
            green_channel = arr[:, :, 1]
            blue_channel = arr[:, :, 2]
            
            # Count pixels that are bright (white background)
            white_pixels = np.sum((arr > 200).all(axis=2))
            total_pixels = arr.shape[0] * arr.shape[1]
            white_ratio = white_pixels / total_pixels
            
            # Count pixels that are very red (red dots)
            red_pixels = np.sum((red_channel > 200) & (green_channel < 100) & (blue_channel < 100))
            red_ratio = red_pixels / total_pixels
            
            print(f"  White background ratio: {white_ratio:.2%}")
            print(f"  Red pixel ratio: {red_ratio:.2%}")
            
            if white_ratio > 0.7:
                print(f"  ⚠ Likely a visualization image (mostly white background)")
        
        # Try MediaPipe landmark extraction
        try:
            landmarks = extract_hand_landmarks(img)
            if landmarks is not None:
                print(f"  ✓ Landmarks extracted successfully: {landmarks.shape}")
                print(f"    Wrist position: {landmarks[0]}")
            else:
                print(f"  ✗ No hand detected by MediaPipe")
                
            features = get_hand_features(img, include_geometric=True)
            if features is not None:
                print(f"  ✓ Features: {len(features)} dimensions")
            else:
                print(f"  ✗ No features extracted")
                
        except Exception as e:
            print(f"  Error: {e}")

print("\n" + "=" * 80)
print("Analysis complete.")
