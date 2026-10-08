@echo off
echo ========================================
echo CIRP Mobile App - Phone Setup
echo ========================================
echo.

echo [1/3] Setting up ADB port forwarding...
adb reverse tcp:8000 tcp:8000
adb reverse tcp:8001 tcp:8001
echo Done!
echo.

echo [2/3] Checking backend server...
curl -s http://localhost:8000/api/v1/health/ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Backend is running at http://localhost:8000
) else (
    echo WARNING: Backend not running! Start it first.
)
echo.

echo [3/3] Starting Flutter app on phone...
cd mobile
flutter run -d R9AN9139KVJ --release

echo.
echo Setup complete!
pause
