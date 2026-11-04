@echo off
echo Setting up ADB reverse port forwarding...
echo.

echo Checking connected devices...
adb devices
echo.

echo Setting up port forwarding for Backend (port 3002)...
adb -s R9AN9139KVJ reverse tcp:3002 tcp:3002
if %ERRORLEVEL% EQU 0 (
    echo ✓ Backend port 3002 forwarded successfully
) else (
    echo ✗ Failed to forward backend port 3002
)
echo.

echo Setting up port forwarding for AI Service (port 8001)...
adb -s R9AN9139KVJ reverse tcp:8001 tcp:8001
if %ERRORLEVEL% EQU 0 (
    echo ✓ AI Service port 8001 forwarded successfully
) else (
    echo ✗ Failed to forward AI Service port 8001
)
echo.

echo Verifying port forwarding...
adb -s R9AN9139KVJ reverse --list
echo.

echo Port forwarding setup complete!
echo.
echo You can now login from the mobile app.
echo.
pause
