@echo off
echo ========================================
echo   CIRP - Full System with Mobile App
echo ========================================
echo.
echo Your PC IP: 10.102.4.204
echo Phone should connect to: http://10.102.4.204:8000
echo.

echo [1/5] Starting Backend API (Django) - Network Mode...
start "Backend API" cmd /k "cd backend && venv\Scripts\activate && python manage.py runserver 0.0.0.0:8000"
timeout /t 5 /nobreak >nul

echo [2/5] Starting AI Service (FastAPI) - Network Mode...
start "AI Service" cmd /k "cd ai && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 5 /nobreak >nul

echo [3/5] Starting Admin Page (Next.js)...
start "Admin Page" cmd /k "cd admin_page && npm run dev"
timeout /t 5 /nobreak >nul

echo [4/5] Connecting to Phone via ADB...
echo Make sure Wireless Debugging is ON on your phone!
adb connect 10.102.4.206:5555
timeout /t 2 /nobreak >nul

echo [5/5] Starting Mobile App on Phone (Flutter)...
start "Mobile App" cmd /k "cd mobile && flutter run"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Backend API:     http://10.102.4.204:8000  (Network Access)
echo AI Service:      http://10.102.4.204:8001  (Network Access)
echo Admin Page:      http://localhost:3000
echo Mobile App:      Running on your phone
echo.
echo Phone Connected: Check your phone screen!
echo.
echo TIPS FOR MOBILE APP:
echo  - Press 'r' in Mobile App terminal for hot reload
echo  - Press 'R' for hot restart
echo  - Press 'q' to quit mobile app
echo.
echo Services running in separate windows.
echo Close each window to stop individual services.
echo.
pause
