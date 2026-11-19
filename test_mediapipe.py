"""
Test MediaPipe hand detection on a sample image.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'host'))

from core.hand_landmarks import (
    _MEDIAPIPE_AVAILABLE,
    _MEDIAPIPE_VERSION,
    extract_hand_landmarks,
    get_hand_features
)
import numpy as np
from PIL import Image

print(f"MediaPipe Available: {_MEDIAPIPE_AVAILABLE}")
print(f"MediaPipe Version: {_MEDIAPIPE_VERSION}")

# Test 1: Create a simple white image
print("\n--- Test 1: White image (no hand expected) ---")
white_image = np.ones((480, 640, 3), dtype=np.uint8) * 255
result = extract_hand_landmarks(white_image)
print(f"Result: {result}")

# Test 2: Try to load an actual dataset image if available
print("\n--- Test 2: Check dataset structure ---")
dataset_path = "storage/uploads"
if os.path.exists(dataset_path):
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(root, file)
                print(f"\nFound image: {img_path}")
                try:
                    img = Image.open(img_path).convert('RGB')
                    print(f"  Size: {img.size}")
                    print(f"  Mode: {img.mode}")
                    
                    # Try landmark extraction
                    landmarks = extract_hand_landmarks(img)
                    if landmarks is not None:
                        print(f"  ✓ Landmarks extracted: shape {landmarks.shape}")
                        print(f"    Sample landmarks (wrist): {landmarks[0]}")
                        print(f"    Sample landmarks (thumb tip): {landmarks[4]}")
                    else:
                        print(f"  ✗ No landmarks detected")
                    
                    # Try full feature extraction
                    features = get_hand_features(img, include_geometric=True)
                    if features is not None:
                        print(f"  ✓ Features extracted: {len(features)} dimensions")
                    else:
                        print(f"  ✗ No features extracted")
                        
                except Exception as e:
                    print(f"  Error: {e}")
                
                # Only test first 3 images
                break
        if files:
            break
else:
    print(f"Dataset path not found: {dataset_path}")

print("\n--- Test Complete ---")
