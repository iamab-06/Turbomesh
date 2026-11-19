# Camera Detection Fix - Visual Diagrams

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              dashboard.html (Frontend)                  │ │
│  │                                                          │ │
│  │  ┌──────────────┐    ┌──────────────┐                 │ │
│  │  │ checkModel   │    │ startCamera  │                 │ │
│  │  │ Status()     │───▶│ Detection()  │                 │ │
│  │  └──────────────┘    └──────────────┘                 │ │
│  │         │                    │                          │ │
│  │         │                    │                          │ │
│  │         ▼                    ▼                          │ │
│  │  ┌──────────────┐    ┌──────────────┐                 │ │
│  │  │ GET /api/    │    │ runDetection │                 │ │
│  │  │ model-status │    │ Loop()       │                 │ │
│  │  └──────────────┘    └──────────────┘                 │ │
│  │                              │                          │ │
│  └──────────────────────────────┼──────────────────────────┘ │
│                                 │                            │
└─────────────────────────────────┼────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             ▼             │
                    │  ┌──────────────────┐    │
                    │  │ POST /api/infer  │    │
                    │  └──────────────────┘    │
                    │            │              │
┌───────────────────┼────────────┼──────────────┼──────────────┐
│                   │            ▼              │              │
│  User Backend     │  ┌──────────────────┐    │              │
│  (FastAPI)        │  │ main.py          │    │              │
│                   │  │                  │    │              │
│                   │  │ ┌──────────────┐ │    │              │
│                   │  │ │ /api/model-  │ │    │              │
│                   └──┼▶│ status       │ │    │              │
│                      │ └──────────────┘ │    │              │
│                      │        │          │    │              │
│                      │        ▼          │    │              │
│                      │ ┌──────────────┐ │    │              │
│                      │ │ Check        │ │    │              │
│                      │ │ loaded_model │ │◀───┘              │
│                      │ └──────────────┘ │                   │
│                      │        │          │                   │
│                      │        ▼          │                   │
│                      │ ┌──────────────┐ │                   │
│                      │ │ Return       │ │                   │
│                      │ │ Status JSON  │ │                   │
│                      │ └──────────────┘ │                   │
│                      └──────────────────┘                   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ core/hand_sign_inference.py                        │    │
│  │                                                      │    │
│  │  ┌──────────────┐  ┌──────────────┐               │    │
│  │  │ load_model() │  │ infer()      │               │    │
│  │  └──────────────┘  └──────────────┘               │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Request Flow - Before Fix

```
User clicks "START CAMERA"
    │
    ▼
┌────────────────────────┐
│ Browser requests       │
│ camera access          │
└────────────────────────┘
    │
    ▼
┌────────────────────────┐
│ Camera stream starts   │
└────────────────────────┘
    │
    ▼
┌────────────────────────────────┐
│ Detection loop begins          │
│ (30 FPS = 30 calls/second)    │
└────────────────────────────────┘
    │
    │  ┌──────────────────────────┐
    └─▶│ Capture frame            │
       └──────────────────────────┘
           │
           ▼
       ┌──────────────────────────┐
       │ POST /api/infer          │
       │ { frame_data: "..." }    │
       └──────────────────────────┘
           │
           ▼
       ┌──────────────────────────┐
       │ Backend checks model     │
       │ loaded_model == None     │
       └──────────────────────────┘
           │
           ▼
       ┌──────────────────────────┐
       │ ❌ 400 Bad Request       │
       │ "No model loaded"        │
       └──────────────────────────┘
           │
           ▼
       ┌──────────────────────────┐
       │ Frontend catches error   │
       │ console.error(...)       │
       └──────────────────────────┘
           │
           │ (Error caught, but loop continues)
           │
           └─────────────┐
                        │
                        ▼
    ┌────────────────────────────────┐
    │ requestAnimationFrame(loop)    │ ◀───┐
    └────────────────────────────────┘     │
           │                                │
           └────────────────────────────────┘
           
    INFINITE LOOP - 30 errors per second!
```

## Request Flow - After Fix

```
User loads dashboard
    │
    ▼
┌─────────────────────────────────┐
│ checkStatus() on page load      │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ GET /api/model-status           │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Backend checks loaded_model     │
└─────────────────────────────────┘
    │
    ├───────────────┬───────────────┐
    │               │               │
    ▼               ▼               ▼
┌────────┐  ┌──────────┐  ┌─────────────┐
│ null   │  │ loading  │  │ loaded      │
└────────┘  └──────────┘  └─────────────┘
    │               │               │
    ▼               ▼               ▼
┌────────┐  ┌──────────┐  ┌─────────────┐
│⚠Yellow │  │⏳ Blue   │  │✓ Green      │
│Warning │  │Pending   │  │Ready        │
└────────┘  └──────────┘  └─────────────┘
    │                              │
    │                              │
    │ User clicks "START CAMERA"  │
    │                              │
    ▼                              ▼
┌────────────────────┐   ┌──────────────────────┐
│ Pre-flight check   │   │ Pre-flight check     │
│ Model loaded? ❌   │   │ Model loaded? ✅     │
└────────────────────┘   └──────────────────────┘
    │                              │
    ▼                              ▼
┌────────────────────┐   ┌──────────────────────┐
│ ⚠ Show warning    │   │ Request camera       │
│ Return early       │   └──────────────────────┘
└────────────────────┘              │
                                    ▼
                         ┌──────────────────────┐
                         │ Camera starts        │
                         └──────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Detection loop       │
                         └──────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌──────────┐         ┌──────────┐         ┌──────────┐
       │ Frame 1  │         │ Frame 2  │         │ Frame 3  │
       │ Success  │         │ Success  │         │ ERROR    │
       └──────────┘         └──────────┘         └──────────┘
              │                     │                     │
              │                     │                     ▼
              │                     │            ┌──────────────┐
              │                     │            │ Error count++│
              │                     │            │ Count: 1     │
              │                     │            └──────────────┘
              │                     │                     │
              └─────────────────────┴─────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Continue loop        │
                         └──────────────────────┘
                                    
       If 3 consecutive errors:
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Stop detection       │
                         │ Show error message   │
                         │ ✗ Camera stopped     │
                         └──────────────────────┘
```

## State Machine Diagram

```
                        ┌─────────────────┐
                        │  Page Load      │
                        └────────┬────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │ Check Model Status     │
                    └────────┬───────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                                  │
            ▼                                  ▼
   ┌─────────────────┐              ┌──────────────────┐
   │ No Model Loaded │              │ Model Loaded     │
   │ (⚠ Yellow)     │              │ (✓ Green)        │
   └────────┬────────┘              └────────┬─────────┘
            │                                 │
            │ User clicks                     │ User clicks
            │ START CAMERA                    │ START CAMERA
            │                                 │
            ▼                                 ▼
   ┌─────────────────┐              ┌──────────────────┐
   │ Show Warning    │              │ Request Camera   │
   │ Block Start     │              └────────┬─────────┘
   └─────────────────┘                       │
                                              ▼
                                    ┌──────────────────┐
                                    │ Camera Active    │
                                    │ Detection Loop   │
                                    └────────┬─────────┘
                                             │
                         ┌───────────────────┼───────────────────┐
                         │                   │                   │
                         ▼                   ▼                   ▼
                ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                │ Success     │    │ Error (1-2) │    │ Error (3+)  │
                │ Reset count │    │ Count error │    │ Stop Camera │
                └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
                       │                  │                   │
                       │                  │                   ▼
                       │                  │          ┌─────────────────┐
                       │                  │          │ Show Error      │
                       │                  │          │ (✗ Red)         │
                       │                  │          └─────────────────┘
                       │                  │
                       └──────────────────┘
                                │
                                ▼
                     ┌──────────────────┐
                     │ Continue Loop    │
                     └──────────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────┐
│                  Detection Loop                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │ Capture      │
                  │ Frame        │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ POST /api/   │
                  │ infer        │
                  └──────┬───────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
    ┌─────────┐                   ┌───────────┐
    │ Success │                   │ Error     │
    └────┬────┘                   └─────┬─────┘
         │                               │
         ▼                               ▼
    ┌─────────────────┐         ┌────────────────┐
    │ consecutiveErrors│         │ consecutiveErrors│
    │ = 0              │         │ ++               │
    └────┬────────────┘         └────────┬────────┘
         │                               │
         │                               ▼
         │                      ┌────────────────────┐
         │                      │ Check count        │
         │                      │ > MAX (3) ?        │
         │                      └────────┬───────────┘
         │                               │
         │              ┌────────────────┴────────────────┐
         │              │                                 │
         │              ▼ No                              ▼ Yes
         │      ┌──────────────┐                  ┌─────────────┐
         │      │ Log error    │                  │ STOP LOOP   │
         │      │ Continue     │                  │ Show error  │
         │      └──────────────┘                  │ Update UI   │
         │                                        └─────────────┘
         │
         └──────────────┬──────────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ requestAnimation  │
              │ Frame(loop)       │
              └───────────────────┘
                        │
                        └──────────┐
                                   │
                                   ▼
                        (Back to Capture Frame)
```

## UI Status Indicators

```
┌──────────────────────────────────────────────────────────────┐
│                    Dashboard UI                               │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Camera Status Indicator                                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  State: NO_MODEL                                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ⚠ No model loaded - Complete a training job to         │  │
│  │   enable detection                                      │  │
│  │   [Background: Yellow/Amber rgba(251, 191, 36, 0.1)]   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  State: MODEL_READY                                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ✓ Model loaded (10 classes) - Ready to start camera   │  │
│  │   [Background: Green rgba(16, 185, 129, 0.1)]          │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  State: CAMERA_ACTIVE                                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ✓ Camera Active - Detecting hand signs...             │  │
│  │   [Background: Green rgba(16, 185, 129, 0.1)]          │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  State: ERROR                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ✗ Detection stopped: Error message here                │  │
│  │   [Background: Red rgba(239, 68, 68, 0.1)]             │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  State: STOPPED                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ○ Camera stopped                                        │  │
│  │   [Background: Gray rgba(148, 163, 184, 0.1)]          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Component Interaction Timeline

```
Time   │ User         │ Frontend           │ Backend        │ Model
───────┼──────────────┼────────────────────┼────────────────┼──────────
  0s   │ Load page    │                    │                │
       │              │ GET /api/status    │                │
       │              │ ◀────────────────▶ │ Return OK     │
       │              │ GET /api/model-    │                │
       │              │     status         │                │
       │              │ ◀────────────────▶ │ Check model   │ Not loaded
       │              │                    │ Return false   │
       │              │ Show ⚠ warning    │                │
       │              │                    │                │
  5s   │ Click START  │ Pre-flight check   │                │
       │ CAMERA       │ GET /api/model-    │                │
       │              │     status         │                │
       │              │ ◀────────────────▶ │ Return false   │ Not loaded
       │              │ Block & warn       │                │
       │              │                    │                │
 30s   │ Complete     │                    │ Receive model  │
       │ training     │                    │ Load model     │ ✓ Loaded
       │              │ Callback triggered │                │
       │              │ checkModelStatus() │                │
       │              │ GET /api/model-    │                │
       │              │     status         │                │
       │              │ ◀────────────────▶ │ Return true    │ Ready
       │              │ Show ✓ ready      │                │
       │              │                    │                │
 35s   │ Click START  │ Pre-flight check   │                │
       │ CAMERA       │ GET /api/model-    │                │
       │              │     status         │                │
       │              │ ◀────────────────▶ │ Return true    │ Ready
       │              │ ✓ Start camera    │                │
       │              │ Request webcam     │                │
       │ Grant        │ ◀────────────────▶ │                │
       │ permission   │                    │                │
       │              │ Start loop         │                │
       │              │                    │                │
 36s   │              │ Capture frame 1    │                │
       │              │ POST /api/infer    │                │
       │              │ ────────────────▶  │ Extract        │
       │              │                    │ landmarks      │ Predict
       │              │ ◀────────────────  │ Return result  │
       │              │ Update UI          │                │
       │              │                    │                │
37-60s │              │ Capture frames...  │ Infer...       │ Predict...
       │              │ ◀──────────────▶   │                │
       │              │                    │                │
 60s   │ Click STOP   │ Stop camera        │                │
       │ CAMERA       │ Release stream     │                │
       │              │ Show ○ stopped    │                │
───────┴──────────────┴────────────────────┴────────────────┴──────────
```

## Data Flow Diagram

```
┌─────────────┐
│  User Image │ (Webcam)
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Canvas Element   │ (640x480)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ toDataURL()      │ Convert to base64 JPEG
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ JSON Request     │ { frame_data: "...", width: 640, height: 480 }
└──────┬───────────┘
       │
       ▼ POST /api/infer
┌──────────────────┐
│ Backend          │
│ main.py          │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ base64.decode()  │ Decode image
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ cv2.imdecode()   │ Convert to numpy array (BGR)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ landmark_infer() │
│ (inference.py)   │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ MediaPipe Hands                                       │
│ - Detect hand landmarks (21 points x 3D)             │
│ - Normalize landmarks                                 │
│ - Extract geometric features (fingertip distances)   │
│ - Flatten to 78-dimensional vector                   │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────┐
│ RandomForest     │ Trained model
│ Model.predict()  │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ Results                                       │
│ {                                             │
│   predicted_class: "5",                      │
│   confidence: 0.95,                          │
│   hand_detected: true,                       │
│   probabilities: { "0": 0.01, "5": 0.95 ... }│
│ }                                             │
└──────┬────────────────────────────────────────┘
       │
       ▼ JSON Response
┌──────────────────┐
│ Frontend         │
│ updateUI()       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Display Results  │
│ - Detected sign  │
│ - Confidence bar │
│ - Inference time │
└──────────────────┘
```

## Legend

```
Symbols:
  ✓  Success / Ready
  ⚠  Warning
  ✗  Error
  ○  Neutral / Stopped
  ⏳ Processing / Pending
  
Colors:
  🟢 Green  - Success, Ready, Active
  🟡 Yellow - Warning, Action Required
  🔴 Red    - Error, Failed
  🔵 Gray   - Stopped, Inactive
  
Flow:
  ───▶  Process flow
  ◀──▶  Request/Response
  │     Sequence
  ▼     Next step
```
