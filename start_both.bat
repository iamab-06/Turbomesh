@echo off
echo ================================================
echo    TurboMesh - Starting Host and User
echo ================================================
echo.

:: Start Host in new window
echo Starting Host on port 8000...
start "TurboMesh Host" cmd /k "cd host && python main.py --host 0.0.0.0 --port 8000"
timeout /t 2 /nobreak > nul

:: Start User in new window
echo Starting User on port 9001...
start "TurboMesh User" cmd /k "cd user && python main.py --host 0.0.0.0 --port 9001"
timeout /t 2 /nobreak > nul

echo.
echo ================================================
echo    Both services starting...
echo ================================================
echo.
echo Host Dashboard: http://localhost:8000
echo User Dashboard: http://localhost:9001
echo.
echo Wait a few seconds, then open both URLs in your browser.
echo.
echo To connect them:
echo   1. Get pairing code from Host dashboard
echo   2. On User dashboard, enter:
echo      - Host IP: 127.0.0.1
echo      - Port: 8000
echo      - Pairing Code: (from host)
echo   3. Click CONNECT TO HOST
echo   4. Approve on Host dashboard
echo.
echo Press any key to open both dashboards in browser...
pause > nul

:: Open in default browser
start http://localhost:8000
start http://localhost:9001

echo.
echo Both dashboards opened!
echo Close this window if you're done.
pause
