@echo off
echo ========================================
echo   CIRP Mobile App - Port Setup
echo ========================================
echo.
echo Setting up port forwarding for your phone...
echo.

adb reverse tcp:8000 tcp:8000
if %errorlevel% neq 0 (
    echo ERROR: Failed to setup port 8000
    pause
    exit /b 1
)
echo [OK] Port 8000 forwarded (Backend API)

adb reverse tcp:8001 tcp:8001
if %errorlevel% neq 0 (
    echo ERROR: Failed to setup port 8001
    pause
    exit /b 1
)
echo [OK] Port 8001 forwarded (AI Service)

echo.
echo ========================================
echo   Port forwarding setup complete!
echo ========================================
echo.
echo Your phone can now access:
echo   - Backend API: localhost:8000
echo   - AI Service:  localhost:8001
echo.
echo The app should now work on your phone!
echo You can now log in with:
echo   Email: citizen@test.com
echo   Password: Test@123
echo.
pause
