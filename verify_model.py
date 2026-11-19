"""
Verify the trained model can be loaded and used for inference.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'host'))

import pickle
import json
import numpy as np
from PIL import Image
from core.hand_landmarks import get_hand_features

# Load model and metadata
model_path = 'test_training_run/output/hand_sign_model.pkl'
metadata_path = 'test_training_run/output/hand_sign_metadata.json'

print("=" * 70)
print("MODEL VERIFICATION")
print("=" * 70)

# Load model
print("\n[1/3] Loading model...")
with open(model_path, 'rb') as f:
    model = pickle.load(f)
print(f"[OK] Model loaded: {type(model).__name__}")

# Load metadata
with open(metadata_path, 'r') as f:
    metadata = json.load(f)
print(f"[OK] Metadata loaded")
print(f"  Model: {metadata['model_name']}")
print(f"  Version: {metadata['model_version']}")
print(f"  Classes: {metadata['num_classes']}")

# Test with a sample image
print("\n[2/3] Testing inference on sample image...")
dataset_dir = 'test_training_run/input/extracted_dataset/ASL Digits/asl_dataset_digits'

# Find a sample image from class 0
class_0_dir = os.path.join(dataset_dir, '0')
sample_images = [f for f in os.listdir(class_0_dir) if f.endswith('.jpeg')][:5]

successful_tests = 0
for img_file in sample_images:
    img_path = os.path.join(class_0_dir, img_file)
    
    try:
        # Load image and extract features
        image = Image.open(img_path).convert('RGB')
        features = get_hand_features(image, include_geometric=True)
        
        if features is not None:
            # Predict
            features_2d = features.reshape(1, -1)
            prediction = model.predict(features_2d)[0]
            probabilities = model.predict_proba(features_2d)[0]
            confidence = probabilities[prediction]
            
            predicted_class = metadata['classes'][str(prediction)]
            
            print(f"  Image: {img_file}")
            print(f"    Features extracted: {len(features)}")
            print(f"    Predicted class: {predicted_class}")
            print(f"    Confidence: {confidence:.2%}")
            print(f"    Top 3 predictions: {[(metadata['classes'][str(i)], p) for i, p in sorted(enumerate(probabilities), key=lambda x: x[1], reverse=True)[:3]]}")
            successful_tests += 1
            break  # Only test one successful image
        else:
            print(f"  Image: {img_file} - No hand detected (skipping)")
    except Exception as e:
        print(f"  Image: {img_file} - Error: {e}")

if successful_tests > 0:
    print("\n[OK] Inference successful!")
else:
    print("\n[ERROR] No successful inferences!")

# Verify model properties
print("\n[3/3] Verifying model properties...")
print(f"  Estimators: {model.n_estimators}")
print(f"  Max depth: {model.max_depth}")
print(f"  Number of features: {model.n_features_in_}")
print(f"  Number of classes: {model.n_classes_}")
print(f"  Classes: {model.classes_}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
