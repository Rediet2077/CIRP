@echo off
echo ========================================
echo   Restarting CIRP Backend
echo ========================================
echo.

echo [1] Stopping existing backend...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq CIRP Backend*" 2>nul
timeout /t 2 /nobreak >nul

echo [2] Starting backend on port 3000...
cd /d "%~dp0backend"
start "CIRP Backend" cmd /k "npm start"
timeout /t 5 /nobreak >nul

echo [3] Testing backend health...
curl -s http://localhost:3000/health
echo.
echo.

echo [4] Testing categories endpoint...
curl -s http://localhost:3000/api/categories
echo.
echo.

echo ========================================
echo   Backend Restarted!
echo ========================================
echo.
echo If you see categories above, backend is working.
echo If you see empty {}, backend needs more time to start.
echo.
echo Now refresh your admin dashboard at:
echo http://localhost:3001
echo.
pause
