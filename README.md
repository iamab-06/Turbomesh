# TurboMesh

A complete, production-structured, end-to-end distributed application for remote GPU processing.

TurboMesh allows a User computer to send files over a local network to a Host computer, which performs AI/GPU processing (Object Detection, Image Similarity) and returns the output.

## Architecture
- **Host (/host)**: Fast API backend running on the GPU machine. Handles LAN IP detection, PyTorch GPU detection, pairing requests, chunked uploads, background processing, and WebSocket updates.
- **User (/user)**: Fast API backend with a web dashboard running locally on the user's machine. Connects to the host, performs chunked uploads, streams results back to the browser.

## Setup and Installation

### Prerequisites
- Python 3.9+
- A local network (Wi-Fi/LAN)
- Two separate machines (optional, but required for the two-computer test)

### 1. Host Setup
\\\ash
cd host
pip install -r ../requirements/host.txt
python main.py --port 8000
\\\`n*The Host dashboard will be available at http://localhost:8000. It will display the Host IP and Pairing Code.*

### 2. User Setup
\\\ash
cd user
pip install -r ../requirements/user.txt
python main.py --port 8001
\\\`n*The User dashboard will be available at http://localhost:8001.*

## Workflow & Two-Computer Testing Procedure
1. Start the Host on Computer B. Note the Host IP and Pairing Code displayed on the dashboard.
2. Start the User on Computer A. Open the User dashboard (http://localhost:8001).
3. Enter the Host IP, Port (8000), and Pairing Code, and click Connect.
4. On the Host dashboard (Computer B), a pending request will appear. Click ALLOW.
5. On the User dashboard (Computer A), the connection will be authenticated.
6. Select an operation (e.g., Object Detection), choose an image file, and create the job.
7. The file will be transferred in chunks to the Host, verified with SHA-256, and processed by YOLOv8.
8. Once complete, the annotated image and JSON analytics will be displayed on the User dashboard.

## Features
- **Hardware Detection**: Automatically detects CUDA, MPS (Apple Silicon), or CPU.
- **Security**: Device pairing with 6-digit codes, explicit Host approval, JWT-like access tokens, and job isolation.
- **File Integrity**: SHA-256 checksum verification and chunked uploads with retry logic.
- **AI Processing**: YOLOv8 Object Detection (vehicle counting, color estimation, plate blurring) and Image Similarity (SSIM, perceptual hash, ResNet-18 embeddings).

