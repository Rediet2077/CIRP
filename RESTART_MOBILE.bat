@echo off
echo ========================================
echo   Restarting Mobile App
echo ========================================
echo.

cd /d "%~dp0mobile"

echo Starting Flutter app on device R9AN9139KVJ...
echo.
start "CIRP Mobile App" cmd /k "flutter run -d R9AN9139KVJ"

echo.
echo Mobile app terminal opened!
echo.
pause
