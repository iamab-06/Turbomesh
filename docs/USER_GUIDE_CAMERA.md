# User Guide: Camera Detection Feature

## Quick Start

### Prerequisites
1. Connect to a TurboMesh host
2. Complete a training job
3. Wait for model to load

### Using Camera Detection

#### Step 1: Check Model Status
When you load the dashboard, look for the camera status indicator:

- ✅ **Green**: "Model loaded (X classes) - Ready to start camera"
  - You're ready to go! Click "START CAMERA"

- ⚠️ **Yellow**: "No model loaded - Complete a training job to enable detection"
  - You need to train a model first

#### Step 2: Start Camera
1. Click the **"START CAMERA"** button
2. Grant camera permissions when prompted
3. The camera feed will appear
4. Hand signs will be detected in real-time

#### Step 3: View Results
The dashboard shows:
- **Detected Sign**: The recognized hand sign
- **Confidence**: How confident the model is (0-100%)
- **Inference Time**: How long detection took (in milliseconds)
- **FPS**: Frames per second being processed

## Troubleshooting

### "No model loaded" Warning

**Problem**: Yellow warning appears when loading dashboard

**Solution**: 
1. Go to the "Train Model" section
2. Upload your training images
3. Start a training job
4. Wait for completion
5. Model will load automatically

### Camera Won't Start

**Problem**: Clicking "START CAMERA" does nothing or shows a warning

**Possible Causes**:

1. **No model loaded**
   - Status shows: "⚠ No model loaded"
   - Solution: Complete a training job first

2. **Camera permission denied**
   - Status shows: "✗ Camera permission denied"
   - Solution: 
     - Click the camera icon in browser address bar
     - Allow camera access
     - Refresh the page
     - Try again

3. **Camera in use by another app**
   - Status shows: "✗ Camera is in use"
   - Solution:
     - Close other apps using camera (Zoom, Teams, etc.)
     - Refresh the page
     - Try again

4. **No camera found**
   - Status shows: "✗ No camera device found"
   - Solution:
     - Check that your camera is connected
     - Try a different USB port
     - Check device manager (Windows) or system preferences (Mac)

### Detection Stops Unexpectedly

**Problem**: Camera was working but suddenly stopped

**Possible Causes**:

1. **Connection lost**
   - Check your internet connection
   - Verify host is still running
   - Refresh the page

2. **Model unloaded**
   - Host may have restarted
   - Need to reload model
   - Complete a training job again

3. **Browser issue**
   - Try refreshing the page
   - Clear browser cache
   - Try a different browser

### Poor Detection Accuracy

**Problem**: Model doesn't recognize hand signs correctly

**Solutions**:
1. **Improve lighting**: Ensure good lighting on your hand
2. **Clean background**: Use a plain background
3. **Proper distance**: Keep hand at consistent distance from camera
4. **Retrain model**: Use more/better training images
5. **Check training data**: Ensure training images are high quality

### Low FPS / Slow Performance

**Problem**: Detection is slow (low FPS number)

**Solutions**:
1. **Close other tabs**: Free up browser resources
2. **Close other apps**: Free up CPU/RAM
3. **Lower resolution**: Use lower camera resolution
4. **Better hardware**: Use a more powerful computer
5. **Update browser**: Ensure browser is up to date

## Browser Support

### Recommended Browsers
- ✅ Chrome 90+
- ✅ Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+

### Requirements
- HTTPS or localhost (required for camera access)
- JavaScript enabled
- Camera permissions granted

### Not Supported
- Internet Explorer
- Very old browser versions
- Browsers without MediaStream API support

## Status Indicators Guide

### Camera Status Colors

| Color | Icon | Meaning | Action |
|-------|------|---------|--------|
| 🟢 Green | ✓ | Ready / Active | You can start camera or it's already running |
| 🟡 Yellow | ⚠ | Warning | Complete required action (e.g., train model) |
| 🔴 Red | ✗ | Error | Check error message and fix issue |
| 🔵 Gray | ○ | Stopped | Camera is not active |

### Example Status Messages

**Initial States**:
- `✓ Model loaded (10 classes) - Ready to start camera` 🟢
- `⚠ No model loaded - Complete a training job to enable detection` 🟡

**Camera Active**:
- `✓ Camera Active - Detecting hand signs...` 🟢

**Errors**:
- `✗ Camera permission denied. Please allow access in browser settings.` 🔴
- `✗ No camera device found.` 🔴
- `✗ Detection stopped: Connection lost` 🔴

**Stopped**:
- `○ Camera stopped` 🔵

## Tips for Best Results

### 1. Training
- Use diverse hand positions
- Include different lighting conditions
- Take at least 50+ images per sign
- Use consistent backgrounds

### 2. Detection
- Position hand in center of frame
- Keep hand clearly visible
- Maintain steady position for 1-2 seconds
- Avoid rapid movements

### 3. Environment
- Good, even lighting
- Plain background (solid color preferred)
- Minimize shadows
- Stable camera position

### 4. Performance
- Close unnecessary browser tabs
- Use wired connection instead of WiFi when possible
- Ensure host machine has adequate resources
- Keep browser updated

## Keyboard Shortcuts

Currently no keyboard shortcuts are implemented, but you can use:
- **Mouse click**: Start/stop camera
- **Browser refresh (F5)**: Reset if something goes wrong

## Privacy & Security

### Camera Access
- Your camera feed is processed locally in your browser
- Frames are sent to the host for inference only
- No video is recorded or stored
- You can revoke camera permission anytime

### Data Handling
- Only individual frames are sent (not continuous video)
- Frames are immediately discarded after inference
- No personal data is collected
- Training data remains on your machine until uploaded

## Getting Help

### Check These First
1. Browser console (F12) for error messages
2. Model status indicator
3. Network connection
4. Camera permissions

### Common Error Messages

**"No model loaded. Please complete a training job and load a model before using camera detection."**
- You need to train a model first
- Go to training section and create a model

**"Your browser does not support camera access"**
- Use a modern browser (Chrome, Firefox, Safari, Edge)
- Ensure you're on HTTPS or localhost

**"Camera is in use by another application"**
- Close other apps using the camera
- Check task manager for camera-using processes

## FAQ

**Q: Why do I need to train a model first?**
A: The camera detection uses your custom-trained model to recognize hand signs. Without training, there's nothing to detect.

**Q: How long does training take?**
A: Typically 1-5 minutes depending on dataset size and host hardware.

**Q: Can I use my phone's camera?**
A: Yes, if you access the dashboard from your phone's browser and grant camera permissions.

**Q: Why is detection slow?**
A: Detection speed depends on host hardware, network latency, and model complexity. Typical speeds are 10-30 FPS.

**Q: Can I detect multiple hands?**
A: Currently, only single-hand detection is supported.

**Q: How do I improve accuracy?**
A: Use more training images, better lighting, consistent backgrounds, and clear hand positions.

**Q: Is my video saved anywhere?**
A: No, only individual frames are processed and immediately discarded.

**Q: Can I use this offline?**
A: You need a connection to the host machine, but the host can be on your local network.

## Next Steps

1. ✅ Connect to host
2. ✅ Complete training job
3. ✅ Start camera detection
4. 🎯 Improve your model with more training data
5. 🎯 Experiment with different hand signs
6. 🎯 Share your results!

---

**Need more help?** Check the technical documentation or contact support.
