import os
import json
import zipfile
import shutil
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as transforms
from torchvision import models
import numpy as np
from PIL import Image
from core.hardware import get_hardware_info

hw = get_hardware_info()
DEVICE = hw['device']


class HandSignDataset(Dataset):
    """Custom dataset for hand sign images."""
    
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.images = []
        self.labels = []
        self.class_to_idx = {}
        self.idx_to_class = {}
        
        # Inspect dataset structure: look for class subdirectories
        class_dirs = sorted([d for d in os.listdir(root_dir) 
                           if os.path.isdir(os.path.join(root_dir, d)) and not d.startswith('.')])
        
        if not class_dirs:
            raise Exception('No class directories found in dataset. Expected structure: dataset/class_name/image.jpg')
        
        for idx, class_name in enumerate(class_dirs):
            self.class_to_idx[class_name] = idx
            self.idx_to_class[idx] = class_name
            
            class_path = os.path.join(root_dir, class_name)
            for img_file in os.listdir(class_path):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    self.images.append(os.path.join(class_path, img_file))
                    self.labels.append(idx)
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]
        label = self.labels[idx]
        
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, label
        except Exception as e:
            raise Exception(f'Failed to load image {img_path}: {str(e)}')


def extract_and_validate_dataset(zip_path, extract_dir):
    """Extract dataset ZIP and validate structure."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except Exception as e:
        raise Exception(f'Failed to extract ZIP: {str(e)}')
    
    # Find actual dataset directory by looking for directories with images
    dataset_dir = None
    
    # Strategy 1: Check if root has image-containing subdirectories
    root_items = os.listdir(extract_dir)
    root_has_class_dirs = False
    
    for item in root_items:
        item_path = os.path.join(extract_dir, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            has_images = any(
                f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))
                for f in os.listdir(item_path)
                if os.path.isfile(os.path.join(item_path, f))
            )
            if has_images:
                root_has_class_dirs = True
                dataset_dir = extract_dir
                break
    
    # Strategy 2: If not found at root, look one level deeper for nested structure
    if not root_has_class_dirs:
        for item in root_items:
            item_path = os.path.join(extract_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                # Check if this directory has subdirs with images
                sub_items = os.listdir(item_path)
                for sub_item in sub_items:
                    sub_path = os.path.join(item_path, sub_item)
                    if os.path.isdir(sub_path) and not sub_item.startswith('.'):
                        has_images = any(
                            f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))
                            for f in os.listdir(sub_path)
                            if os.path.isfile(os.path.join(sub_path, f))
                        )
                        if has_images:
                            dataset_dir = item_path
                            break
                if dataset_dir:
                    break
    
    if not dataset_dir:
        raise Exception('No valid dataset structure found. Expected: class_dir/image files')
    
    # Validate dataset structure
    class_dirs = [d for d in os.listdir(dataset_dir) 
                 if os.path.isdir(os.path.join(dataset_dir, d)) and not d.startswith('.')]
    
    if not class_dirs:
        raise Exception('No class directories found. Expected structure: class_name/image.jpg')
    
    total_images = 0
    for class_dir in class_dirs:
        class_path = os.path.join(dataset_dir, class_dir)
        images = [f for f in os.listdir(class_path) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
        if not images:
            raise Exception(f'Class directory {class_dir} has no images')
        total_images += len(images)
    
    return dataset_dir, class_dirs, total_images


def train_hand_sign_model(dataset_dir, job, output_dir):
    """Train a hand sign recognition model."""
    
    # Define transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Load dataset
    job['stage'] = 'Loading dataset'
    job['progress'] = 20
    
    dataset = HandSignDataset(dataset_dir, transform=train_transform)
    num_classes = len(dataset.class_to_idx)
    
    if len(dataset) == 0:
        raise Exception('Dataset is empty')
    
    # Split into train/val
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    # Apply val transform to val dataset
    val_dataset.dataset.transform = val_transform
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    
    # Load pre-trained ResNet50 (more accurate than MobileNetV2)
    job['stage'] = 'Loading pre-trained model'
    job['progress'] = 25
    
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    # Replace final classification layer
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.to(DEVICE)
    
    # Training setup - train all layers for better accuracy
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)  # Lower LR for fine-tuning
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)
    
    num_epochs = 15  # Increased for better convergence
    best_val_acc = 0.0
    training_history = []
    
    # Training loop
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
            
            progress = 25 + (epoch + (batch_idx + 1) / len(train_loader)) / num_epochs * 50
            job['progress'] = int(progress)
            job['stage'] = f'Training: Epoch {epoch + 1}/{num_epochs}'
        
        train_loss /= len(train_loader)
        train_acc = 100 * train_correct / train_total
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = 100 * val_correct / val_total
        
        training_history.append({
            'epoch': epoch + 1,
            'train_loss': round(float(train_loss), 4),
            'train_accuracy': round(float(train_acc), 2),
            'val_loss': round(float(val_loss), 4),
            'val_accuracy': round(float(val_acc), 2)
        })
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
        
        scheduler.step()
    
    # Save model
    job['stage'] = 'Saving model'
    job['progress'] = 85
    
    model_path = os.path.join(output_dir, 'hand_sign_model.pt')
    # Save state dict with all tensors moved to CPU to ensure portability across devices
    # (CUDA→MPS, MPS→CUDA, etc.). The loader will move to the appropriate device.
    cpu_state_dict = {k: v.cpu() if isinstance(v, torch.Tensor) else v 
                      for k, v in model.state_dict().items()}
    torch.save(cpu_state_dict, model_path)
    
    # Generate metadata
    job['stage'] = 'Generating metadata'
    job['progress'] = 90
    
    metadata = {
        'model_name': 'Hand Sign Recognition Model',
        'model_version': '2.0.0',
        'model_architecture': 'ResNet50',
        'num_classes': num_classes,
        'classes': dataset.idx_to_class,
        'class_to_index': dataset.class_to_idx,
        'input_size': 224,
        'preprocessing': {
            'normalize_mean': [0.485, 0.456, 0.406],
            'normalize_std': [0.229, 0.224, 0.225],
            'resize': 224,
            'input_channels': 3
        },
        'training': {
            'epochs': num_epochs,
            'batch_size': 16,
            'optimizer': 'Adam',
            'learning_rate': 0.0001,
            'loss_function': 'CrossEntropyLoss',
            'train_test_split': 0.8,
            'device': DEVICE,
            'notes': 'Fine-tuned ResNet50 with all layers trainable for better accuracy'
        },
        'metrics': {
            'best_validation_accuracy': round(float(best_val_acc), 2),
            'training_history': training_history
        },
        'inference': {
            'framework': 'PyTorch',
            'input_format': 'RGB image (224x224)',
            'output_format': 'class probabilities',
            'confidence_threshold': 0.5
        }
    }
    
    metadata_path = os.path.join(output_dir, 'hand_sign_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    return ['hand_sign_model.pt', 'hand_sign_metadata.json']


def run_hand_sign_recognition(job, input_dir, output_dir):
    """Main handler for hand sign recognition job."""
    
    # GPU requirement check: Host must use GPU for training efficiency
    if DEVICE == 'cpu':
        raise Exception(
            f'GPU required for hand sign training. Available device: {DEVICE}. '
            'Host must have CUDA (Windows/Linux) or MPS (Apple Silicon) GPU available.'
        )
    
    files = list(job['files'].keys())
    if len(files) != 1:
        raise Exception('Hand Sign Recognition requires exactly 1 dataset file (ZIP)')
    
    zip_path = os.path.join(input_dir, files[0])
    
    if not zip_path.lower().endswith('.zip'):
        raise Exception('Dataset must be a ZIP file')
    
    # Validate it's actually a ZIP
    if not zipfile.is_zipfile(zip_path):
        raise Exception('Invalid ZIP file')
    
    # Extract and validate dataset
    job['stage'] = 'Extracting dataset'
    job['progress'] = 10
    
    extract_dir = os.path.join(input_dir, 'extracted_dataset')
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        dataset_dir, class_dirs, total_images = extract_and_validate_dataset(zip_path, extract_dir)
    except Exception as e:
        shutil.rmtree(extract_dir, ignore_errors=True)
        raise Exception(f'Dataset validation failed: {str(e)}')
    
    job['stage'] = f'Dataset validated: {len(class_dirs)} classes, {total_images} images'
    job['progress'] = 15
    
    try:
        result_files = train_hand_sign_model(dataset_dir, job, output_dir)
    except Exception as e:
        shutil.rmtree(extract_dir, ignore_errors=True)
        raise Exception(f'Model training failed: {str(e)}')
    finally:
        shutil.rmtree(extract_dir, ignore_errors=True)
    
    return result_files
