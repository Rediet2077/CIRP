@echo off
echo ================================================
echo  CIRP MOBILE FIX - Windows Firewall Rule
echo  THIS MUST RUN AS ADMINISTRATOR
echo ================================================
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must run as Administrator!
    echo.
    echo RIGHT-CLICK this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Running as Administrator... OK
echo.
echo Creating firewall rule for port 3000...
netsh advfirewall firewall add rule name="CIRP Backend Port 3000" dir=in action=allow protocol=TCP localport=3000

echo.
echo Firewall rule created!
echo.
echo Testing backend access...
curl -s http://192.168.8.60:3000/health
echo.
echo.

if %errorLevel% equ 0 (
    echo ================================================
    echo  SUCCESS! Mobile app should work now!
    echo ================================================
    echo.
    echo Next steps:
    echo 1. Close CIRP app on your phone completely
    echo 2. Reopen CIRP app
    echo 3. Try login again
    echo.
) else (
    echo ================================================
    echo  WARNING: Could not verify backend access
    echo  But firewall rule was created
    echo ================================================
    echo.
    echo Try mobile app anyway - it might work!
    echo.
)

pause
