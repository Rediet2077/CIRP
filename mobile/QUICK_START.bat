@echo off
echo ========================================
echo   CIRP Mobile App - Quick Start
echo ========================================
echo.

echo Step 1: Checking Flutter...
flutter --version
echo.

echo Step 2: Checking connected devices...
flutter devices
echo.

echo Step 3: Getting dependencies...
cd /d "%~dp0"
call flutter pub get
echo.

echo ========================================
echo Ready to run!
echo ========================================
echo.
echo Make sure:
echo  1. Your phone is connected via USB
echo  2. USB debugging is enabled
echo  3. You updated the IP in lib/core/config/api_config.dart
echo  4. Backend is running on 0.0.0.0:8000
echo.
echo Press any key to run the app...
pause >nul

echo.
echo Running app...
flutter run --hot

pause
