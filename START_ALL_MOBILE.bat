@echo off
echo ========================================
echo   CIRP - Full System with Mobile App
echo ========================================
echo.

echo [1/4] Starting Backend API (Django)...
start "Backend API" cmd /k "cd backend && venv\Scripts\activate && python manage.py runserver"
timeout /t 3 /nobreak >nul

echo [2/4] Starting AI Service (FastAPI)...
start "AI Service" cmd /k "cd ai && uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 3 /nobreak >nul

echo [3/4] Starting Admin Page (Next.js)...
start "Admin Page" cmd /k "cd admin_page && npm run dev"
timeout /t 3 /nobreak >nul

echo [4/4] Starting Mobile App (Flutter Web)...
start "Mobile App" cmd /k "cd mobile && python -m http.server 8080 --directory build\web"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Backend API:     http://localhost:8000
echo AI Service:      http://localhost:8001
echo Admin Page:      http://localhost:3000
echo Mobile App:      http://localhost:8080
echo.
echo New Photo-First Workflow:
echo  1. 📸 Take Photo (FIRST)
echo  2. 📍 Set Location
echo  3. 📝 Fill Details (AI suggests category)
echo  4. ✅ Review and Submit
echo.
echo Features Active:
echo  ✅ Photo-first workflow
echo  ✅ All photos accepted (no quality check)
echo  ✅ AI classification (90%+ accuracy)
echo  ✅ Duplicate detection (80%% threshold)
echo  ✅ Message: "This report was reported by another user"
echo.
echo Opening mobile app...
timeout /t 3 /nobreak >nul
start http://localhost:8080
echo.
echo Press any key to exit...
pause >nul
