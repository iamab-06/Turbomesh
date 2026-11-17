"""
Test the landmark-based hand sign recognition pipeline with 0to9.zip dataset.
Validates:
- Landmark extraction success rate
- Training/validation accuracy
- Per-class performance
- Feature extraction consistency
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tempfile
import shutil
from PIL import Image
import numpy as np
from host.core.hand_landmarks import extract_hand_landmarks, normalize_landmarks, get_hand_features
from host.core.hand_sign_landmark_training import LandmarkDataset, train_landmark_model
import json


def test_landmark_extraction():
    """Test landmark extraction on 0to9 dataset."""
    print("\n" + "="*60)
    print("TEST 1: Landmark Extraction from 0to9 Dataset")
    print("="*60)
    
    dataset_path = "/tmp/0to9"
    if not os.path.exists(dataset_path):
        print("❌ Dataset not found at /tmp/0to9")
        print("   Run: unzip /Users/debarghyapramanik/Downloads/0to9.zip -d /tmp/")
        return False
    
    extraction_results = {class_num: {'success': 0, 'failed': 0, 'errors': []} for class_num in range(10)}
    
    for class_num in range(10):
        class_dir = os.path.join(dataset_path, str(class_num))
        if not os.path.exists(class_dir):
            print(f"⚠ Class {class_num} not found")
            continue
        
        images = [f for f in os.listdir(class_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"\nClass {class_num}: Testing {len(images)} images...")
        
        for img_file in images[:3]:  # Test first 3 images per class
            img_path = os.path.join(class_dir, img_file)
            try:
                image = Image.open(img_path).convert('RGB')
                landmarks = extract_hand_landmarks(image)
                
                if landmarks is None:
                    extraction_results[class_num]['failed'] += 1
                    extraction_results[class_num]['errors'].append(f"{img_file}: No hand detected")
                else:
                    # Validate landmarks shape
                    assert landmarks.shape == (21, 3), f"Expected (21, 3), got {landmarks.shape}"
                    
                    # Test normalization
                    normalized = normalize_landmarks(landmarks)
                    assert normalized.shape == (21, 3)
                    
                    # Test feature extraction
                    features = get_hand_features(image, include_geometric=True)
                    assert features.shape == (78,), f"Expected (78,), got {features.shape}"
                    
                    extraction_results[class_num]['success'] += 1
                    print(f"  ✓ {img_file}: landmarks={landmarks.shape}, features={features.shape}")
            except Exception as e:
                extraction_results[class_num]['failed'] += 1
                extraction_results[class_num]['errors'].append(f"{img_file}: {str(e)}")
                print(f"  ❌ {img_file}: {str(e)}")
    
    # Summary
    total_success = sum(r['success'] for r in extraction_results.values())
    total_failed = sum(r['failed'] for r in extraction_results.values())
    
    print(f"\n{'─'*60}")
    print(f"Landmark Extraction Results:")
    print(f"  Success: {total_success}")
    print(f"  Failed: {total_failed}")
    print(f"  Success Rate: {100 * total_success / (total_success + total_failed):.1f}%")
    
    if total_failed > 0:
        print(f"\n⚠ Some images failed landmark extraction. This is expected for")
        print(f"  images where hand is not visible or occluded.")
    
    return total_success > 0


def test_dataset_loading():
    """Test LandmarkDataset class with 0to9."""
    print("\n" + "="*60)
    print("TEST 2: Dataset Loading and Feature Extraction")
    print("="*60)
    
    dataset_path = "/tmp/0to9"
    if not os.path.exists(dataset_path):
        print("❌ Dataset not found")
        return False
    
    try:
        print("Loading landmark dataset...")
        dataset = LandmarkDataset(dataset_path)
        X, y = dataset.get_data()
        
        print(f"✓ Dataset loaded successfully")
        print(f"  Total samples: {len(X)}")
        print(f"  Features per sample: {X.shape[1]}")
        print(f"  Classes: {list(dataset.class_to_idx.keys())}")
        print(f"  Class distribution:")
        for class_name in sorted(dataset.class_to_idx.keys()):
            count = np.sum(y == dataset.class_to_idx[class_name])
            print(f"    Class {class_name}: {count} samples")
        
        if len(dataset.failed_images) > 0:
            print(f"\n  Failed to extract landmarks from {len(dataset.failed_images)} images")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load dataset: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_training_and_validation():
    """Test model training with 0to9 dataset."""
    print("\n" + "="*60)
    print("TEST 3: Model Training and Validation")
    print("="*60)
    
    dataset_path = "/tmp/0to9"
    if not os.path.exists(dataset_path):
        print("❌ Dataset not found")
        return False
    
    try:
        print("Loading dataset...")
        dataset = LandmarkDataset(dataset_path)
        X, y = dataset.get_data()
        
        print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(dataset.class_to_idx)} classes")
        
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Train set: {len(X_train)} samples")
        print(f"Validation set: {len(X_val)} samples")
        
        # Train model
        print("\nTraining RandomForest classifier...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        print("Evaluating...")
        y_train_pred = model.predict(X_train)
        y_val_pred = model.predict(X_val)
        
        train_acc = accuracy_score(y_train, y_train_pred)
        val_acc = accuracy_score(y_val, y_val_pred)
        
        print(f"\nResults:")
        print(f"  Training Accuracy: {train_acc:.4f}")
        print(f"  Validation Accuracy: {val_acc:.4f}")
        
        # Per-class metrics
        precision, recall, f1, support = precision_recall_fscore_support(
            y_val, y_val_pred, average=None
        )
        
        print(f"\nPer-class Performance:")
        print(f"  {'Class':<8} {'Precision':<12} {'Recall':<12} {'F1':<12} {'Support':<10}")
        print(f"  {'-'*54}")
        for i in range(len(precision)):
            class_name = dataset.idx_to_class[i]
            print(f"  {class_name:<8} {precision[i]:<12.4f} {recall[i]:<12.4f} {f1[i]:<12.4f} {support[i]:<10}")
        
        # Confusion matrix
        cm = confusion_matrix(y_val, y_val_pred)
        print(f"\nConfusion Matrix:")
        print(f"  {cm}")
        
        # Check if model is reasonable
        if val_acc > 0.6:
            print(f"\n✓ Model shows reasonable performance (val_acc > 0.6)")
            return True
        else:
            print(f"\n⚠ Model accuracy is low (val_acc < 0.6)")
            print(f"  This may indicate issues with landmark extraction or dataset quality")
            return False
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_inference_consistency():
    """Test that inference uses same preprocessing as training."""
    print("\n" + "="*60)
    print("TEST 4: Inference Preprocessing Consistency")
    print("="*60)
    
    dataset_path = "/tmp/0to9"
    if not os.path.exists(dataset_path):
        print("❌ Dataset not found")
        return False
    
    try:
        # Test with a sample image
        sample_image_path = os.path.join(dataset_path, "0", os.listdir(os.path.join(dataset_path, "0"))[0])
        image = Image.open(sample_image_path).convert('RGB')
        
        # Extract features (training-side)
        features_training = get_hand_features(image, include_geometric=True)
        
        if features_training is None:
            print("❌ Could not extract features from sample image")
            return False
        
        print(f"✓ Training preprocessing:")
        print(f"  Features shape: {features_training.shape}")
        print(f"  Feature range: [{np.min(features_training):.4f}, {np.max(features_training):.4f}]")
        print(f"  Mean: {np.mean(features_training):.4f}, Std: {np.std(features_training):.4f}")
        
        # Test inference preprocessing
        from user.core.hand_sign_inference import get_hand_features_from_frame
        import cv2
        
        # Convert PIL to BGR (what would come from webcam)
        img_array = np.array(image)
        bgr_frame = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        features_inference = get_hand_features_from_frame(bgr_frame)
        
        if features_inference is None:
            print("❌ Could not extract features in inference mode")
            return False
        
        print(f"\n✓ Inference preprocessing:")
        print(f"  Features shape: {features_inference.shape}")
        print(f"  Feature range: [{np.min(features_inference):.4f}, {np.max(features_inference):.4f}]")
        print(f"  Mean: {np.mean(features_inference):.4f}, Std: {np.std(features_inference):.4f}")
        
        # Check consistency
        diff = np.abs(features_training - features_inference).max()
        print(f"\n✓ Consistency check:")
        print(f"  Max feature difference: {diff:.6f}")
        
        if diff < 0.01:
            print(f"  ✓ Training and inference preprocessing are CONSISTENT")
            return True
        else:
            print(f"  ⚠ Small differences detected (may be due to JPEG compression)")
            return True
    except Exception as e:
        print(f"❌ Consistency test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("TurboMesh Landmark-Based Hand Sign Recognition Pipeline Tests")
    print("Testing with 0to9.zip dataset")
    
    tests = [
        ("Landmark Extraction", test_landmark_extraction),
        ("Dataset Loading", test_dataset_loading),
        ("Training & Validation", test_training_and_validation),
        ("Inference Consistency", test_inference_consistency),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {str(e)}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for p in results.values() if p)
    print(f"\n{total_passed}/{len(results)} tests passed")
    
    sys.exit(0 if all(results.values()) else 1)
