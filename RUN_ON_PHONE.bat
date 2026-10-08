@echo off
echo ========================================
echo CIRP Mobile App - Run on Phone
echo ========================================
echo.

echo Checking if phone is connected...
adb devices | findstr /C:"device" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No phone detected!
    echo Please connect your phone via USB and enable USB debugging.
    pause
    exit /b 1
)
echo Phone connected!
echo.

echo Setting up ADB reverse for localhost access...
adb reverse tcp:8000 tcp:8000
adb reverse tcp:8001 tcp:8001
echo Port forwarding configured!
echo.

echo Starting Flutter app...
cd mobile
flutter run -d R9AN9139KVJ --release

pause
