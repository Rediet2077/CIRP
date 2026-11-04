@echo off
echo ========================================
echo   CIRP - Fresh Restart All Services
echo ========================================
echo.

echo [Step 1] Stopping all existing processes...
taskkill /F /IM node.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *CIRP*" 2>nul
timeout /t 2 /nobreak >nul

echo [Step 2] Starting Backend API (Port 3000)...
start "CIRP Backend" cmd /k "cd /d %~dp0backend && npm start"
timeout /t 5 /nobreak >nul

echo [Step 3] Testing Backend...
curl -s http://localhost:3000/health
echo.

echo [Step 4] Starting AI Service (Port 8001)...
start "CIRP AI Service" cmd /k "cd /d %~dp0ai && uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 3 /nobreak >nul

echo [Step 5] Starting Admin Dashboard (Port 3001)...
cd /d "%~dp0admin page"
start "CIRP Admin Dashboard" cmd /k "npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Backend API:        http://localhost:3000
echo AI Service:         http://localhost:8001  
echo Admin Dashboard:    http://localhost:3001
echo.
echo [Testing Backend Categories...]
timeout /t 2 /nobreak >nul
curl -s http://localhost:3000/api/categories
echo.
echo.
echo ========================================
pause
