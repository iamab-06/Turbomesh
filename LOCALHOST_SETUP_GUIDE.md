# Running TurboMesh Host and User on Same Machine

## Quick Setup Guide

### Step 1: Start Host (Terminal 1)

```powershell
cd host
python main.py --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start User (Terminal 2)

```powershell
cd user
python main.py --host 0.0.0.0 --port 9001
```

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9001
```

### Step 3: Open in Browser

- **Host**: http://localhost:8000
- **User**: http://localhost:9001

### Step 4: Pair Them

**On Host Dashboard (http://localhost:8000):**
1. Look for the "PAIRING CODE" section
2. Note the 6-digit code (e.g., "212358")

**On User Dashboard (http://localhost:9001):**
1. In "Connect to Host" section, enter:
   - **HOST IP ADDRESS**: `127.0.0.1` or `10.0.8.166` (your actual IP)
   - **PORT**: `8000`
   - **PAIRING CODE**: (the code from host)
2. Click **"CONNECT TO HOST"**

**Back on Host Dashboard:**
1. Check "Pending Requests" section
2. You should see a new request
3. Click **"APPROVE"**

**Success!** Both dashboards should now show connected status.

## Troubleshooting

### Issue: "All connection attempts failed"

**Possible causes:**

#### 1. Host not running
**Check:** Is the host terminal still running?
**Fix:** Make sure you started the host first and it's running on port 8000

#### 2. Wrong IP address
**Check:** What IP did you enter in the user app?

For same machine, you can use:
- `127.0.0.1` (localhost)
- `localhost`
- `10.0.8.166` (your actual network IP - if on same network)

**Fix:** Try `127.0.0.1` first

#### 3. Port mismatch
**Check:** 
- Host is on port 8000
- User entered port 8000 in connection form

**Fix:** Make sure both match

#### 4. Firewall blocking
**Check:** Windows Firewall may block the connection

**Fix:**
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "TurboMesh Host" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "TurboMesh User" -Direction Inbound -LocalPort 9001 -Protocol TCP -Action Allow
```

#### 5. Wrong pairing code
**Check:** The pairing code expires after 5 minutes

**Fix:** 
- Refresh the host page to get a new code
- Copy it carefully (all 6 digits)

#### 6. CORS issues (FIXED in latest version)
The code now includes CORS middleware to allow cross-origin requests.

### Issue: Connection works but can't see pending request

**Check:** Did the user app show "pending" status after clicking connect?

**Fix:** 
1. Check both terminal windows for error messages
2. Look for logs like:
   ```
   🔄 Attempting to pair with http://127.0.0.1:8000
   ✓ Pairing request successful
   ```

### Issue: Request stuck in "pending"

**Fix:** Click the "APPROVE" button on the host dashboard

## Testing the Connection

After pairing, test with these steps:

1. **Check connection status**
   - User dashboard should show host IP and connection status
   - Host dashboard should show approved device

2. **Create a test job**
   - On user dashboard, select an operation
   - Upload required files
   - Start the job
   - Watch the progress on both dashboards

## Network Modes

### Mode 1: Localhost (Same Machine)
```
Host: 127.0.0.1:8000
User: 127.0.0.1:9001
Connect with: 127.0.0.1:8000
```
✅ Best for testing
✅ No network required
✅ No firewall issues

### Mode 2: LAN (Same Network)
```
Host: 10.0.8.166:8000
User: 10.0.8.166:9001
Connect with: 10.0.8.166:8000
```
✅ Good for real-world testing
⚠️ May need firewall rules
⚠️ Both must be on same network

### Mode 3: Separate Machines
```
Host: 10.0.8.166:8000 (Machine A)
User: 10.0.8.200:9001 (Machine B)
Connect with: 10.0.8.166:8000
```
✅ Production-like
⚠️ Requires network configuration
⚠️ May need firewall rules

## Logs to Check

### User Terminal
Look for:
```
🔄 Attempting to pair with http://127.0.0.1:8000
   Pairing code: 212358
   Client ID: client_abc12345
✓ Pairing request successful: {'status': 'pending'}
```

### Host Terminal
Look for:
```
INFO:     127.0.0.1:xxxxx - "POST /api/auth/pair HTTP/1.1" 200 OK
```

If you see `400 Bad Request` or `500 Internal Server Error`, check the error details in the logs.

## Common Error Messages

### "Pairing code expired or invalid"
- The code expires after 5 minutes
- Refresh host page to get new code
- Make sure you copied it correctly

### "Cannot connect to host"
- Host is not running
- Wrong IP address
- Firewall blocking
- Port already in use

### "Connection refused"
- Host not started
- Host crashed
- Wrong port number

### "CORS error" (Browser console)
- Fixed in latest version with CORS middleware
- If still seeing this, make sure you updated host/main.py

## Quick Test Commands

### Test if host is reachable
```powershell
# From another terminal
curl http://127.0.0.1:8000/api/host/info
```

Should return JSON with host information.

### Test if user is reachable
```powershell
curl http://127.0.0.1:9001/api/status
```

Should return JSON with status information.

### Check what's running on ports
```powershell
netstat -ano | findstr "8000"
netstat -ano | findstr "9001"
```

Should show LISTENING status.

## Starting Fresh

If things get messy:

1. **Stop both servers** (Ctrl+C in both terminals)

2. **Clear any stuck processes**
```powershell
# Find processes using the ports
netstat -ano | findstr "8000"
netstat -ano | findstr "9001"

# Kill them (use the PID from netstat)
taskkill /PID <pid> /F
```

3. **Restart host first**
```powershell
cd host
python main.py --port 8000
```

4. **Then restart user**
```powershell
cd user
python main.py --port 9001
```

5. **Refresh both browser tabs**

6. **Try pairing again**

## Success Checklist

- [ ] Host running on port 8000
- [ ] User running on port 9001
- [ ] Both accessible in browser
- [ ] Pairing code visible on host
- [ ] Connection attempt from user succeeds
- [ ] Pending request appears on host
- [ ] Approved on host
- [ ] User shows connected status
- [ ] Can create and run jobs

## Still Having Issues?

1. Check both terminal windows for error messages
2. Check browser console (F12) for errors
3. Make sure both apps are up to date
4. Try using `127.0.0.1` instead of IP address
5. Try different ports (e.g., 8080 and 8081)
6. Disable antivirus/firewall temporarily to test
7. Check if another app is using the ports

## Advanced: Running with Custom Ports

```powershell
# Host on custom port
cd host
python main.py --host 0.0.0.0 --port 9000

# User on custom port
cd user
python main.py --host 0.0.0.0 --port 9002

# Connect using: 127.0.0.1:9000
```

Just make sure the ports don't conflict!
