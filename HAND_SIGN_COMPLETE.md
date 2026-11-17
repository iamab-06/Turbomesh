# Hand Sign Detection - Complete Implementation

## Overview
Complete end-to-end hand sign recognition system with automatic model training and real-time camera detection.

## Architecture

### 1. **Dataset Upload**
- User uploads a `.zip` file containing hand sign images
- Expected structure: `dataset/class_name/image.jpg`
- Example: `signs.zip` → `rock/img001.jpg`, `paper/img002.jpg`, `scissors/img003.jpg`

### 2. **Host-Side Training (GPU)**
Located in: `host/core/hand_sign_training.py`

**Process:**
- Extracts and validates dataset structure
- Loads images into PyTorch DataLoader
- Uses **MobileNetV2** with transfer learning
- Trains for 10 epochs with:
  - Adam optimizer (lr=0.001)
  - CrossEntropyLoss
  - 80/20 train/val split
  - Data augmentation (flip, rotation)
- Runs on **Apple Silicon MPS / CUDA / CPU**

**Output Files:**
- `hand_sign_model.pt` - Trained PyTorch model
- `hand_sign_metadata.json` - Model config, classes, preprocessing params, training metrics

### 3. **Automatic Model Loading**
Located in: `user/templates/dashboard.html` (JavaScript)

**When training completes:**
1. Downloads `.pt` model file from host
2. Downloads metadata JSON
3. POSTs to `/api/load-model` endpoint
4. User server loads model into memory
5. Model ready for inference

### 4. **Real-Time Camera Detection**
Located in: `user/main.py` + `dashboard.html`

**Process:**
- Camera opens automatically after model loads
- Captures frames via WebRTC (getUserMedia)
- Preprocessing:
  - Resize to 224×224
  - Normalize with ImageNet mean/std
  - Convert to tensor
- Sends to `/api/infer` endpoint
- Displays results in real-time:
  - Detected hand sign
  - Confidence percentage
  - FPS counter
  - Inference time (ms)

## User Workflow

### Step 1: Connect to Host
1. Enter Host IP and pairing code
2. Host approves connection
3. Dashboard appears

### Step 2: Train Model
1. Select **"Hand Sign Recognition - Train Model"**
2. Choose `.zip` dataset file
3. Click **"Create Job & Upload"**
4. Wait for training (progress shown)

### Step 3: Automatic Detection
1. Training completes → Results displayed
2. Model automatically downloads
3. Camera opens immediately
4. Real-time hand sign detection begins
5. See detected signs with confidence scores

## Key Features

✅ **Three Job Options Only:**
- Object Detection & Image Analytics
- Image Similarity / Duplicate Detection
- Hand Sign Recognition - Train Model

✅ **Automatic Camera Launch:**
- No manual buttons needed
- Camera opens when metadata is received
- Uses trained model immediately

✅ **Full GPU Training:**
- Host processes .zip with PyTorch
- Transfer learning with MobileNetV2
- Validation accuracy tracking

✅ **Real-Time Inference:**
- Browser-based camera access
- Client-side preprocessing
- Fast inference on user machine

## Technical Stack

**Backend:**
- FastAPI (Host + User servers)
- PyTorch + TorchVision
- MobileNetV2 architecture
- Apple Silicon MPS / CUDA support

**Frontend:**
- Vanilla JavaScript
- WebRTC getUserMedia API
- Canvas for image preprocessing
- Real-time WebSocket updates

**Data Pipeline:**
- ZIP extraction and validation
- PyTorch Dataset/DataLoader
- Chunked file uploads with SHA-256 verification
- WebSocket progress monitoring

## File Structure

```
host/
  core/
    hand_sign_training.py    # Model training logic
    processing.py            # Job processing dispatcher
    worker.py                # Background job executor
  main.py                    # Host FastAPI server

user/
  templates/
    dashboard.html           # Main UI with camera detection
    inference.html           # Standalone detection page
  main.py                    # User FastAPI server with /api/infer

storage/
  {job_id}/
    input/                   # Uploaded .zip
    output/
      hand_sign_model.pt     # Trained model
      hand_sign_metadata.json # Model metadata
```

## API Endpoints

**Host (port 8000):**
- `GET /api/host/info` - Hardware info
- `POST /api/jobs` - Create training job
- `POST /api/jobs/{id}/upload/chunk` - Upload file chunks
- `POST /api/jobs/{id}/upload/finalize` - Finalize upload
- `GET /api/jobs/{id}/result/{file}` - Download result files
- `WS /ws/jobs/{id}` - Real-time progress updates

**User (port 8001):**
- `GET /` - Main dashboard
- `POST /api/load-model` - Load trained model into memory
- `POST /api/infer` - Run inference on image data
- `GET /api/jobs/{id}/result/{file}` - Proxy to host

## Metadata Schema

```json
{
  "model_name": "Hand Sign Recognition Model",
  "model_architecture": "MobileNetV2",
  "num_classes": 3,
  "classes": {
    "0": "rock",
    "1": "paper",
    "2": "scissors"
  },
  "input_size": 224,
  "preprocessing": {
    "normalize_mean": [0.485, 0.456, 0.406],
    "normalize_std": [0.229, 0.224, 0.225]
  },
  "metrics": {
    "best_validation_accuracy": 95.5,
    "training_history": [...]
  }
}
```

## Running the System

**Start Host:**
```bash
cd host
python main.py --port 8000
```

**Start User:**
```bash
cd user
python main.py --port 8001
```

**Access:**
- Host Dashboard: http://localhost:8000
- User Dashboard: http://localhost:8001

## Current Status

✅ Host server running on port 8000
✅ User server running on port 8001  
✅ Apple Silicon MPS GPU detected
✅ All dependencies installed
✅ Complete training pipeline implemented
✅ Real-time camera detection implemented
✅ Automatic model loading after training
✅ Three job options configured correctly

**Ready for testing with real hand sign dataset!**
