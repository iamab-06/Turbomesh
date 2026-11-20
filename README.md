# TurboMesh ⚡

A complete, production-grade distributed application for remote GPU-accelerated computer vision and AI processing across a local network (LAN) or single-machine setup.

TurboMesh separates computation between a **Host** node (which handles heavy AI workloads such as object detection, deep image similarity, and hand landmark training) and a **User** node (which provides an interactive, modern web dashboard for users to submit jobs, stream results, and run real-time camera inference).

---

## 🌟 Key Features

- **Distributed Architecture**: Clean separation between Host (GPU computation node) and User (client dashboard).
- **Secure LAN Device Pairing**: 6-digit one-time pairing code system with explicit host approval and session authentication.
- **Resilient File Ingestion**: Chunked uploads with SHA-256 integrity verification, automatic retry, and job isolation.
- **Computer Vision & AI Workloads**:
  - **Object Detection (YOLOv8)**: Real-time inference with bounding boxes, confidence scoring, vehicle/object counts, and image annotation.
  - **Deep Image Similarity**: Multi-modal image comparison combining deep embeddings (ResNet-18), Structural Similarity (SSIM), perceptual hashing (pHash/dHash), and ORB feature matching.
  - **Hand Sign & Landmark Recognition**: Automated dataset ingestion, MediaPipe 21-point 3D landmark extraction, classifier training (Random Forest / MLP), and real-time live webcam gesture classification.
  - **AI Image Generation (Prompt-to-Image)**: GPU/CPU-accelerated text-to-image synthesis with semantic prompt understanding, artistic style presets (Cyberpunk, Space, Sunset, Nature, Oceanic, Synthwave, Fantasy, Cinematic, Monochrome), customizable resolutions, and seed variations.
- **Live WebSocket Streaming**: Real-time progress updates, logs, and preview streaming between Host and User interfaces.
- **Hardware Acceleration**: Automatic runtime detection and utilization of NVIDIA CUDA, Apple Silicon MPS, or fallback CPU.

---

## 🏗 Architecture

```
                   +--------------------------------------------+
                   |                 LOCAL AREA NETWORK         |
                   |                                            |
+--------------------------+                         +--------------------------+
|      USER MACHINE        |                         |       HOST MACHINE       |
|    (Port 8001 / Web UI)  |                         |    (Port 8000 / GPU API) |
|                          |    1. Pair (6-digit)    |                          |
|  - Web Dashboard         | ----------------------> |  - Auth & Device Manager |
|  - Real-time Webcam      | <---------------------- |  - Chunked File Storage  |
|  - WebSocket Client      |    2. Token Issued      |  - YOLOv8 Inference      |
|  - Client Job Manager    |                         |  - Deep Similarity       |
|                          |    3. Chunked Upload    |  - MediaPipe Landmark &  |
|                          | ----------------------> |    Classifier Training   |
|                          | <---------------------- |  - WebSocket Dispatcher  |
|                          |    4. Stream Progress   |                          |
+--------------------------+                         +--------------------------+
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.9+
- A modern web browser (Chrome, Firefox, Edge, Safari)
- Optional: NVIDIA GPU with CUDA drivers (for accelerated inference and training)

---

### Step 1: Install Dependencies

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iamab-06/Turbomesh.git
   cd Turbomesh
   ```

2. **Setup virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install requirements:**
   ```bash
   # For the Host node:
   pip install -r requirements/host.txt

   # For the User node:
   pip install -r requirements/user.txt
   ```

---

### Step 2: Running on a Single Machine (Localhost)

You can run both nodes side-by-side on your local machine:

#### Windows One-Click Launch:
Double-click `start_both.bat` or run:
```cmd
start_both.bat
```

#### Or Run in Two Separate Terminals:

**Terminal 1 — Start the Host:**
```bash
cd host
python main.py --port 8000
```
> The Host dashboard will open at `http://localhost:8000`. Note the **Pairing Code** displayed on the screen.

**Terminal 2 — Start the User:**
```bash
cd user
python main.py --port 8001
```
> The User dashboard will open at `http://localhost:8001`.

---

### Step 3: Running Across Two Computers (LAN Setup)

1. **Host Computer (Computer with GPU)**:
   - Start the host service: `cd host && python main.py --host 0.0.0.0 --port 8000`
   - Check the Host Dashboard (`http://localhost:8000`) for the **LAN IP** (e.g., `192.168.1.50`) and the active **Pairing Code**.
2. **User Computer**:
   - Start the user service: `cd user && python main.py --port 8001`
   - Open `http://localhost:8001`.
   - Enter the Host's IP address (`192.168.1.50`), port `8000`, and the 6-digit pairing code.
   - Click **Connect**.
3. **Approval**:
   - On the Host Dashboard, click **ALLOW** on the incoming pairing prompt.
   - The User Dashboard will transition to the connected workspace.

---

## 🛠 Usage & Workloads

### 1. Object Detection
- Upload any image file (`.jpg`, `.png`).
- Host runs YOLOv8 detection, annotates bounding boxes, computes class statistics, and returns the annotated image and analytics payload.

### 2. Deep Image Similarity
- Submit a reference image and a target image.
- Computes cosine similarity across ResNet feature vectors, SSIM structural difference map, perceptual hash distance, and ORB keypoint correspondences.

### 3. Hand Sign Landmark Training & Live Inference
- **Training**: Upload a ZIP archive containing labeled hand sign directories. The Host extracts 21 MediaPipe hand landmarks per frame, computes normalized coordinates, and trains a classifier with live progress streaming.
- **Real-Time Webcam Inference**: Open the User Dashboard's camera tab to stream live frames through the trained hand sign model with real-time classification overlays.

### 4. AI Image Generation (Prompt-to-Image)
- **Prompt Input & Styling**: The client sends descriptive text prompts (e.g. *"A cyberpunk neon metropolis with flying cars and rain reflections"*), selecting optional style presets (Cyberpunk, Cosmic Space, Sunset, Nature, Oceanic, Synthwave, Fantasy, Cinematic, Monochrome), target resolutions, and seeds.
- **Host GPU Synthesis**: The Host processes the request using its GPU-accelerated PyTorch neural latent art synthesizer, constructing spatial coordinate grids, Fourier frequency embeddings, atmospheric composition layers, and lighting bloom.
- **Image Return & Metadata**: The Host generates `generated_image.png` and `generation_metadata.json`, which are returned to the User dashboard with high-resolution preview, download options, and quick variation regeneration.

---

## 📁 Repository Structure

```text
Turbomesh/
├── host/                    # Host GPU application
│   ├── api/                 # FastAPI routes (auth, pairing, jobs, streaming)
│   ├── core/                # Core AI logic (detection, similarity, landmark pipeline)
│   ├── static/              # Host UI assets
│   ├── templates/           # Host web templates
│   └── main.py              # Host entry point
├── user/                    # User client application
│   ├── api/                 # User local API routes
│   ├── core/                # Upload managers & real-time inference client
│   ├── static/              # Dashboard styling & JS logic
│   ├── templates/           # User web dashboard
│   └── main.py              # User entry point
├── requirements/            # Dependency definitions
│   ├── host.txt             # Host requirements (PyTorch, Ultralytics, MediaPipe, OpenCV)
│   └── user.txt             # User requirements (FastAPI, Uvicorn, Requests, WebSockets)
├── tests/                   # Automated unit & integration tests
├── delete_jobs.sh           # Storage & job cleanup utility
├── start_both.bat           # Windows single-click launcher
├── .gitignore               # Ignored build, weights, and temporary artifacts
└── README.md                # Comprehensive documentation
```

---

## 🛡 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
