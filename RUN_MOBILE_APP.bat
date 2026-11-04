@echo off
echo.
echo ========================================
echo CIRP Mobile App Launcher
echo ========================================
echo.

cd "%~dp0mobile"

echo [1/4] Checking Flutter installation...
flutter --version
if %errorlevel% neq 0 (
    echo ERROR: Flutter is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo [2/4] Getting Flutter dependencies...
flutter pub get
if %errorlevel% neq 0 (
    echo ERROR: Failed to get dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Launching Android Emulator (Pixel 7a)...
start /B flutter emulators --launch Pixel_7a

echo Waiting 30 seconds for emulator to boot...
timeout /t 30 /nobreak

echo.
echo [4/4] Running CIRP Mobile App...
echo.
echo NOTE: The app will connect to backend at http://10.0.2.2:3002
echo       (Android Emulator bridge to localhost:3002)
echo.

flutter run

pause
