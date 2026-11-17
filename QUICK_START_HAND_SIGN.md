# Hand Sign Recognition Job - Quick Start

## For Users

### How to Train a Hand Sign Model

1. **Connect to Host**
   - Open User dashboard at `http://localhost:8001`
   - Enter Host IP, Port, and Pairing Code
   - Click CONNECT
   - Wait for approval on Host

2. **Create Hand Sign Recognition Job**
   - Select "Hand Sign Recognition - Train Model (1 ZIP dataset)"
   - Choose your Kaggle hand sign dataset ZIP file
   - Click CREATE JOB & UPLOAD

3. **Wait for Training**
   - Watch the upload progress
   - Watch the training progress (Epoch 1/10 → 10/10)
   - Status updates in real time

4. **Download Trained Model**
   - Once complete, results appear
   - Download `hand_sign_model.pt` (weights)
   - Download `hand_sign_metadata.json` (class mappings)

### Using Your Trained Model

```python
import torch
import json
from torchvision import models, transforms
from PIL import Image

# Load metadata
with open('hand_sign_metadata.json') as f:
    metadata = json.load(f)

# Load model
model = models.mobilenet_v2()
model.classifier[1] = torch.nn.Linear(1280, metadata['num_classes'])
model.load_state_dict(torch.load('hand_sign_model.pt'))
model.eval()

# Prepare image
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=metadata['preprocessing']['normalize_mean'],
        std=metadata['preprocessing']['normalize_std']
    )
])

# Infer
img = Image.open('hand_sign.jpg').convert('RGB')
with torch.no_grad():
    output = model(transform(img).unsqueeze(0))
    pred_idx = torch.argmax(output[0]).item()
    pred_class = metadata['classes'][str(pred_idx)]
    confidence = torch.softmax(output[0], dim=0)[pred_idx].item()

print(f"Predicted: {pred_class}")
print(f"Confidence: {confidence:.2%}")
```

## Dataset Requirements

### Format
- ZIP file containing class subdirectories
- Each subdirectory contains images for that class

### Example Structure
```
my_hand_sign_dataset.zip
├── A/
│   ├── image_001.jpg
│   ├── image_002.jpg
│   └── ...
├── B/
│   ├── image_001.jpg
│   ├── image_002.jpg
│   └── ...
└── C/
    ├── image_001.jpg
    └── ...
```

### Image Requirements
- Supported formats: JPG, JPEG, PNG, GIF, BMP
- Minimum resolution: 224x224 (will be resized)
- Recommended: 500+ images per class for good accuracy

### From Kaggle
1. Search for "hand sign" or "ASL" dataset
2. Download as ZIP
3. Upload directly to TurboMesh

## Generated Files

### hand_sign_model.pt
- PyTorch MobileNetV2 weights
- Size: ~8.7 MB
- Load with: `torch.load('hand_sign_model.pt')`

### hand_sign_metadata.json
- Class mappings: `{"0": "A", "1": "B", ...}`
- Preprocessing parameters
- Model architecture info
- Training history and metrics

## Training Information

### Model Architecture
- MobileNetV2 (fast and efficient)
- Transfer learning from ImageNet weights
- Fine-tuned on your dataset

### Training Parameters
- Epochs: 10
- Batch size: 16
- Optimizer: Adam
- Learning rate: 0.001
- Train/validation split: 80/20

### Hardware
- Uses GPU when available (CUDA or MPS)
- Falls back to CPU if needed
- Training time depends on dataset size

### Performance Indicators
- Logged in metadata: `metrics.training_history`
- Shows loss and accuracy per epoch
- Best validation accuracy reported

## For Developers

### Code Location
- Training logic: `host/core/hand_sign_training.py`
- Integration: `host/core/worker.py`
- Processing: `host/core/processing.py`

### Key Classes
- `HandSignDataset`: PyTorch dataset wrapper
- `extract_and_validate_dataset()`: ZIP handling
- `train_hand_sign_model()`: Training logic
- `run_hand_sign_recognition()`: Job handler

### Adding Support for Webcam Inference

In User dashboard (JavaScript):
```javascript
// After downloading model + metadata
const video = document.getElementById('webcam');
const canvas = document.createElement('canvas');
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;

const ctx = canvas.getContext('2d');
ctx.drawImage(video, 0, 0);

// Send canvas data to inference endpoint
const imageData = canvas.toDataURL('image/jpeg');
// POST to /api/infer with imageData + modelId
```

In User backend (Python):
```python
@app.post('/api/infer')
async def infer_hand_sign(image_data: str, model_id: str):
    # Load model from storage
    # Preprocess image
    # Run inference
    # Return class + confidence
```

## Testing

### Run Tests
```bash
cd /path/to/TurboMesh
python3 -m pytest tests/test_e2e.py -v
```

### Expected Output
```
test_pairing_flow PASSED
test_multiple_devices_can_pair_with_same_code PASSED
test_pairing_code_refreshes_after_5_minutes PASSED
test_hand_sign_recognition_job_creation PASSED
test_hand_sign_recognition_file_upload PASSED

5 passed
```

### Test Dataset
- Provided: `tests/test_hand_sign_dataset.zip`
- 3 classes: A, B, C
- 5 images per class
- ~38 KB

## Troubleshooting

### Model Training Fails
- Check: Dataset structure is correct (class_name/images/)
- Check: ZIP file is valid and not corrupted
- Check: At least 2 images per class

### Model Download Fails
- Ensure job completed (Status: COMPLETED)
- Check: Model files exist in job output directory
- Verify: Both .pt and .json files are present

### Inference Gives Wrong Results
- Check: Image size matches 224x224
- Check: Preprocessing uses correct normalization
- Check: Class mapping matches metadata

### GPU Not Used
- Check: CUDA installed and working (for NVIDIA)
- Check: MPS available (for Apple Silicon)
- Check: Sufficient GPU memory (~2 GB)

### Out of Memory
- Reduce batch size in training code (line 194)
- Train on fewer epochs (line 198)
- Use smaller dataset initially

## Performance Tips

1. **Dataset Quality**
   - Clean images, no artifacts
   - Good lighting and contrast
   - Multiple angles per class

2. **Dataset Size**
   - Minimum: 50 images per class
   - Recommended: 500+ images per class
   - More data → better accuracy

3. **Hardware**
   - GPU: 30-60 seconds (2000 images)
   - CPU: 5-10 minutes (2000 images)
   - Use GPU for faster training

4. **Fine-tuning**
   - Current model: general-purpose classes
   - To improve: Add more training data
   - To specialize: Use domain-specific images

## Next Steps

1. ✅ Train hand sign model with your dataset
2. ✅ Evaluate model accuracy from metadata
3. ✅ Use model for inference on new images
4. Optional: Implement webcam inference UI
5. Optional: Fine-tune model with more data

## Support

See full documentation:
- `IMPLEMENTATION_REPORT.md` - Complete implementation details
- `HAND_SIGN_IMPLEMENTATION.md` - Architecture and design
- `tests/test_e2e.py` - Test examples
