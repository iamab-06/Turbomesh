"""
Landmark-based hand sign recognition training.
Uses MediaPipe landmarks (21 points × 3 coordinates + geometric features) 
with Random Forest classifier for robustness on small datasets.
"""

import os
import json
import zipfile
import shutil
import numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import pickle
from core.hardware import get_hardware_info
from core.hand_landmarks import get_hand_features, extract_hand_landmarks

hw = get_hardware_info()
DEVICE = hw['device']


class LandmarkDataset:
    """Dataset manager for landmark-based hand sign recognition."""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.features = []
        self.labels = []
        self.class_to_idx = {}
        self.idx_to_class = {}
        self.failed_images = []
        
        # Get class directories (expect numeric names 0-9)
        class_dirs = sorted([d for d in os.listdir(root_dir) 
                           if os.path.isdir(os.path.join(root_dir, d)) and not d.startswith('.')])
        
        if not class_dirs:
            raise Exception('No class directories found in dataset.')
        
        print(f"Found {len(class_dirs)} classes: {class_dirs}")
        
        for idx, class_name in enumerate(class_dirs):
            self.class_to_idx[class_name] = idx
            self.idx_to_class[idx] = class_name
            
            class_path = os.path.join(root_dir, class_name)
            image_files = [f for f in os.listdir(class_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            print(f"Processing class {class_name}: {len(image_files)} images...")
            
            for img_file in image_files:
                img_path = os.path.join(class_path, img_file)
                try:
                    # Load image and extract landmarks
                    image = Image.open(img_path).convert('RGB')
                    features = get_hand_features(image, include_geometric=True)
                    
                    if features is not None:
                        self.features.append(features)
                        self.labels.append(idx)
                    else:
                        self.failed_images.append((class_name, img_file, "No hand detected"))
                except Exception as e:
                    self.failed_images.append((class_name, img_file, str(e)))
    
    def get_data(self):
        """Return features and labels as numpy arrays."""
        if len(self.features) == 0:
            raise Exception("No valid landmarks extracted from dataset!")
        
        X = np.array(self.features, dtype=np.float32)
        y = np.array(self.labels, dtype=np.int32)
        
        print(f"Extracted {len(X)} valid samples with {X.shape[1]} features per sample")
        
        if self.failed_images:
            print(f"⚠ Failed to extract landmarks from {len(self.failed_images)} images:")
            for class_name, img_file, reason in self.failed_images[:5]:
                print(f"  - {class_name}/{img_file}: {reason}")
            if len(self.failed_images) > 5:
                print(f"  ... and {len(self.failed_images) - 5} more")
        
        return X, y


def extract_and_validate_dataset(zip_path, extract_dir):
    """Extract dataset ZIP and validate structure."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except Exception as e:
        raise Exception(f'Failed to extract ZIP: {str(e)}')
    
    # Find actual dataset directory
    dataset_dir = None
    root_items = os.listdir(extract_dir)
    
    # Check if root has image-containing subdirectories
    for item in root_items:
        item_path = os.path.join(extract_dir, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            has_images = any(
                f.lower().endswith(('.jpg', '.jpeg', '.png'))
                for f in os.listdir(item_path)
                if os.path.isfile(os.path.join(item_path, f))
            )
            if has_images:
                dataset_dir = extract_dir
                break
    
    # If not found at root, look one level deeper
    if not dataset_dir:
        for item in root_items:
            item_path = os.path.join(extract_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                sub_items = os.listdir(item_path)
                for sub_item in sub_items:
                    sub_path = os.path.join(item_path, sub_item)
                    if os.path.isdir(sub_path) and not sub_item.startswith('.'):
                        has_images = any(
                            f.lower().endswith(('.jpg', '.jpeg', '.png'))
                            for f in os.listdir(sub_path)
                            if os.path.isfile(os.path.join(sub_path, f))
                        )
                        if has_images:
                            dataset_dir = item_path
                            break
                if dataset_dir:
                    break
    
    if not dataset_dir:
        raise Exception('No valid dataset structure found.')
    
    return dataset_dir


def train_landmark_model(dataset_dir, job, output_dir):
    """Train Random Forest model on hand landmark features."""
    
    # Load dataset and extract landmarks
    job['stage'] = 'Extracting hand landmarks from dataset'
    job['progress'] = 15
    
    dataset = LandmarkDataset(dataset_dir)
    X, y = dataset.get_data()
    
    job['stage'] = 'Splitting dataset into train/validation'
    job['progress'] = 30
    
    # Stratified split to maintain class distribution
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train set: {X_train.shape[0]} samples")
    print(f"Validation set: {X_val.shape[0]} samples")
    
    # Train Random Forest classifier
    job['stage'] = 'Training Random Forest classifier'
    job['progress'] = 40
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    job['stage'] = 'Evaluating model performance'
    job['progress'] = 70
    
    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)
    
    train_acc = accuracy_score(y_train, y_train_pred)
    val_acc = accuracy_score(y_val, y_val_pred)
    
    print(f"Training accuracy: {train_acc:.4f}")
    print(f"Validation accuracy: {val_acc:.4f}")
    
    # Per-class metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        y_val, y_val_pred, average=None
    )
    
    cm = confusion_matrix(y_val, y_val_pred)
    
    # Save model
    job['stage'] = 'Saving model'
    job['progress'] = 80
    
    model_path = os.path.join(output_dir, 'hand_sign_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Generate metadata
    job['stage'] = 'Generating metadata'
    job['progress'] = 90
    
    metadata = {
        'model_name': 'Hand Sign Recognition (Landmark-based)',
        'model_version': '3.0.0',
        'model_type': 'RandomForest',
        'model_architecture': 'RandomForest(n_estimators=100, max_depth=20)',
        'num_classes': len(dataset.class_to_idx),
        'classes': dataset.idx_to_class,
        'class_to_index': dataset.class_to_idx,
        'feature_extraction': {
            'method': 'MediaPipe Hand Landmarker',
            'landmarks_per_hand': 21,
            'coordinates_per_landmark': 3,
            'base_features': 63,
            'geometric_features': 15,
            'total_features': 78,
            'normalization': 'centered on wrist, scaled by max distance'
        },
        'training': {
            'dataset_size': len(X),
            'train_size': len(X_train),
            'val_size': len(X_val),
            'failed_images': len(dataset.failed_images),
            'train_test_split': 0.8,
            'device': DEVICE
        },
        'metrics': {
            'training_accuracy': float(train_acc),
            'validation_accuracy': float(val_acc),
            'per_class_precision': {dataset.idx_to_class[i]: float(p) 
                                   for i, p in enumerate(precision)},
            'per_class_recall': {dataset.idx_to_class[i]: float(r) 
                                for i, r in enumerate(recall)},
            'per_class_f1': {dataset.idx_to_class[i]: float(f) 
                           for i, f in enumerate(f1)},
            'confusion_matrix': cm.tolist()
        },
        'inference': {
            'framework': 'scikit-learn',
            'input_format': 'hand landmarks (21 points × 3 + geometric features)',
            'output_format': 'class probabilities',
            'confidence_threshold': 0.5,
            'preprocessing': 'MediaPipe landmark extraction + normalization'
        }
    }
    
    metadata_path = os.path.join(output_dir, 'hand_sign_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    return ['hand_sign_model.pkl', 'hand_sign_metadata.json']


def run_hand_sign_recognition(job, input_dir, output_dir):
    """Main handler for hand sign recognition job (landmark-based)."""
    
    # GPU requirement check
    if DEVICE == 'cpu':
        print("⚠ Running on CPU. Landmark extraction may be slower.")
    
    files = list(job['files'].keys())
    if len(files) != 1:
        raise Exception('Hand Sign Recognition requires exactly 1 dataset file (ZIP)')
    
    zip_path = os.path.join(input_dir, files[0])
    
    if not zip_path.lower().endswith('.zip'):
        raise Exception('Dataset must be a ZIP file')
    
    if not zipfile.is_zipfile(zip_path):
        raise Exception('Invalid ZIP file')
    
    # Extract and validate dataset
    job['stage'] = 'Extracting dataset'
    job['progress'] = 10
    
    extract_dir = os.path.join(input_dir, 'extracted_dataset')
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        dataset_dir = extract_and_validate_dataset(zip_path, extract_dir)
    except Exception as e:
        shutil.rmtree(extract_dir, ignore_errors=True)
        raise Exception(f'Dataset validation failed: {str(e)}')
    
    try:
        result_files = train_landmark_model(dataset_dir, job, output_dir)
    except Exception as e:
        shutil.rmtree(extract_dir, ignore_errors=True)
        raise Exception(f'Model training failed: {str(e)}')
    finally:
        shutil.rmtree(extract_dir, ignore_errors=True)
    
    return result_files
