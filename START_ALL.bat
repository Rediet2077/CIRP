@echo off
echo ========================================
echo   CIRP Platform - Starting All Services
echo ========================================
echo.

echo [1/3] Starting Django Backend (Port 8000)...
start "CIRP Backend" cmd /k "cd /d %~dp0backend && python manage.py runserver"
timeout /t 3 /nobreak >nul

echo [2/3] Starting AI Service (Port 8001)...
start "CIRP AI Service" cmd /k "cd /d %~dp0ai && uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Admin Dashboard (Port 3000)...
start "CIRP Admin Dashboard" cmd /k "cd /d %~dp0admin_page && bun run dev"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   All Services Started Successfully!
echo ========================================
echo.
echo Backend API:        http://localhost:8000
echo AI Service:         http://localhost:8001
echo Admin Dashboard:    http://localhost:3000
echo AI Documentation:   http://localhost:8001/docs
echo.
echo Press any key to open API Reference...
pause >nul
start API_REFERENCE.md
