# TurboMesh - Localhost Testing Guide

## Quick Start (30 seconds)

```powershell
# Double-click this file:
start_both.bat

# Or run manually in 2 terminals:
# Terminal 1:
cd host && python main.py --port 8000

# Terminal 2:
cd user && python main.py --port 9001
```

Then open:
- Host: http://localhost:8000
- User: http://localhost:9001

## Pairing (1 minute)

1. **Host** → Copy the 6-digit pairing code
2. **User** → Enter connection details:
   - Host IP: `127.0.0.1`
   - Port: `8000`
   - Pairing Code: (paste from step 1)
3. **User** → Click "CONNECT TO HOST"
4. **Host** → Click "APPROVE" on the pending request
5. ✅ Connected!

## Troubleshooting

### Problem: "All connection attempts failed"

**Run diagnostic**:
```powershell
python test_connection.py
```

**Common fixes**:

1. **Host not running?**
   ```powershell
   cd host
   python main.py --port 8000
   ```

2. **Wrong IP?**
   Use `127.0.0.1` instead of `10.0.8.166` for localhost

3. **Port busy?**
   ```powershell
   # Check what's using port 8000
   netstat -ano | findstr "8000"
   
   # Kill it or use different port
   python main.py --port 8080
   ```

4. **Firewall?**
   ```powershell
   # Run as Administrator
   New-NetFirewallRule -DisplayName "TurboMesh" -Direction Inbound -LocalPort 8000,9001 -Protocol TCP -Action Allow
   ```

5. **Old cache?**
   - Hard refresh: Ctrl+Shift+R
   - Try incognito mode
   - Clear browser cache

### Problem: "Pairing code expired"

- Codes expire after 5 minutes
- Refresh host page to get new code
- Try again

### Problem: Connection works but no pending request

- Check both terminal windows for errors
- Make sure you're using the correct pairing code
- Try refreshing host dashboard

## File Structure

```
TurboMesh_Project/
├── host/
│   ├── main.py                  (Host server - port 8000)
│   ├── core/
│   │   ├── auth.py              (Pairing logic)
│   │   └── ...
│   └── templates/
│       └── dashboard.html
├── user/
│   ├── main.py                  (User server - port 9001)
│   ├── core/
│   │   ├── client.py            (Connection logic)
│   │   └── ...
│   └── templates/
│       └── dashboard.html
├── start_both.bat               (Start both services)
├── test_connection.py           (Diagnostic tool)
└── docs/
    ├── LOCALHOST_SETUP_GUIDE.md         (Detailed guide)
    ├── CAMERA_DETECTION_FIX.md          (Camera issue fix)
    ├── USER_GUIDE_CAMERA.md             (User guide)
    └── CONNECTION_FIX_SUMMARY.md        (Connection fix)
```

## What Got Fixed Recently

### 1. Camera Detection Issue ✅
- **Problem**: Infinite 400 errors when camera started without model
- **Fixed**: Added model status checks and better error handling
- **Details**: See `CAMERA_FIX_SUMMARY.md`

### 2. Connection/CORS Issue ✅
- **Problem**: "All connection attempts failed" when pairing
- **Fixed**: Added CORS middleware to host
- **Details**: See `CONNECTION_FIX_SUMMARY.md`

## Testing Checklist

- [ ] Both services start without errors
- [ ] Can access both dashboards in browser
- [ ] Can see pairing code on host dashboard
- [ ] Can enter connection details on user dashboard
- [ ] Connection request succeeds (shows "pending")
- [ ] Pending request appears on host dashboard
- [ ] Can approve request
- [ ] User dashboard shows connected status
- [ ] Can create a training job
- [ ] Job completes successfully
- [ ] Model loads automatically
- [ ] Camera detection works

## Useful Commands

### Start Services
```powershell
# Easy way
start_both.bat

# Manual way
cd host && python main.py --port 8000
cd user && python main.py --port 9001
```

### Test Connection
```powershell
python test_connection.py

# Or with custom ports
python test_connection.py 127.0.0.1 8080 8081
```

### Check Ports
```powershell
# See what's running
netstat -ano | findstr "8000"
netstat -ano | findstr "9001"
```

### Kill Stuck Process
```powershell
# Get PID from netstat, then:
taskkill /PID <pid> /F
```

### Test Endpoints Directly
```powershell
# Test host
curl http://localhost:8000/api/host/info

# Test user
curl http://localhost:9001/api/status

# Test model status
curl http://localhost:9001/api/model-status
```

## Network Modes

### Mode 1: Localhost (Both on Same Machine)
```
Host: 127.0.0.1:8000
User: 127.0.0.1:9001
Connect with: 127.0.0.1:8000
```
✅ Best for testing
✅ No network issues
✅ No firewall problems

### Mode 2: LAN (Same Network)
```
Host: 10.0.8.166:8000
User: 10.0.8.166:9001
Connect with: 10.0.8.166:8000
```
✅ Real-world testing
⚠️ Need to be on same network
⚠️ May need firewall rules

### Mode 3: Separate Machines
```
Host Machine: 10.0.8.166:8000
User Machine: 10.0.8.200:9001
Connect with: 10.0.8.166:8000
```
✅ Production scenario
⚠️ Requires network setup
⚠️ Firewall configuration

## Security Notes

- Pairing codes expire after 5 minutes
- Tokens are cryptographically secure
- CORS currently allows all origins (fine for testing)
- For production, restrict CORS to specific origins

## Performance Tips

- Close unused browser tabs
- Use wired connection when possible
- Ensure adequate GPU resources for host
- Monitor resource usage in Task Manager

## Common Workflows

### 1. First Time Setup
```
1. Start both services
2. Pair them
3. Upload training data
4. Create training job
5. Wait for model
6. Test camera detection
```

### 2. Daily Development
```
1. Start both services (start_both.bat)
2. They should auto-reconnect if previously paired
3. Run diagnostic if issues: python test_connection.py
4. Develop/test features
```

### 3. Clean Start
```
1. Stop both services (Ctrl+C)
2. Clear any stuck processes
3. Restart host first
4. Restart user second
5. Refresh browsers
6. Re-pair if needed
```

## Logs to Monitor

### User Terminal
Good:
```
🔄 Attempting to pair with http://127.0.0.1:8000
✓ Pairing request successful
INFO: Uvicorn running on http://0.0.0.0:9001
```

Bad:
```
❌ Connection failed
❌ HTTP Error 400
Cannot connect to host
```

### Host Terminal
Good:
```
INFO: "POST /api/auth/pair HTTP/1.1" 200 OK
INFO: "GET /api/clients HTTP/1.1" 200 OK
```

Bad:
```
"POST /api/auth/pair HTTP/1.1" 400 Bad Request
ERROR: Connection refused
```

## Browser Console

Press F12 to open developer tools.

Good:
```
✓ Camera access granted
✓ Model loaded
✓ Connection successful
```

Bad:
```
CORS error
Failed to fetch
Network error
```

## Environment Setup

### Requirements
```
Python 3.8+
FastAPI
Uvicorn
OpenCV (cv2)
NumPy
MediaPipe
httpx
```

### Install Dependencies
```powershell
pip install fastapi uvicorn opencv-python numpy mediapipe httpx
```

## Advanced Configuration

### Custom Ports
```powershell
# Host on port 9000
python host/main.py --port 9000

# User on port 9002
python user/main.py --port 9002

# Connect using 127.0.0.1:9000
```

### Custom Host Address
```powershell
# Bind to specific IP
python host/main.py --host 192.168.1.100 --port 8000
```

### Environment Variables
```powershell
# Set timeout
$env:HTTPX_TIMEOUT = "30"

# Set log level
$env:LOG_LEVEL = "DEBUG"
```

## FAQ

**Q: Can I run both on same machine?**
A: Yes! That's what this guide is for. Use different ports.

**Q: Do I need to restart after pairing once?**
A: No, pairing is persistent. Just restart the services.

**Q: Can I use phone to access dashboards?**
A: Yes, if phone is on same network, use the LAN IP (e.g., 10.0.8.166:8000).

**Q: Why use 127.0.0.1 instead of localhost?**
A: They're the same, but 127.0.0.1 is more explicit and avoids DNS issues.

**Q: How do I know if CORS is working?**
A: Run `python test_connection.py` and check for "✓ CORS is configured".

**Q: What if I get "address already in use"?**
A: Another app is using that port. Use `netstat` to find it or choose different port.

## Support

If stuck:
1. Run `python test_connection.py`
2. Check terminal logs (both host and user)
3. Check browser console (F12)
4. Review LOCALHOST_SETUP_GUIDE.md
5. Check CONNECTION_FIX_SUMMARY.md for recent fixes

## Updates

- **Camera Detection**: Fixed infinite error loop (see CAMERA_FIX_SUMMARY.md)
- **CORS**: Added middleware for cross-origin requests (see CONNECTION_FIX_SUMMARY.md)
- **Error Logging**: Improved error messages throughout
- **Diagnostics**: Added test_connection.py tool

---

**Status**: Ready for testing
**Last Updated**: 2024
**Version**: Latest with CORS fix
