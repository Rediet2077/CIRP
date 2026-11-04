@echo off
echo ==========================================
echo CIRP Network Connection Fix
echo ==========================================
echo.

echo Step 1: Allowing Port 3002 in Windows Firewall...
netsh advfirewall firewall delete rule name="CIRP Backend Port 3002"
netsh advfirewall firewall add rule name="CIRP Backend Port 3002" dir=in action=allow protocol=TCP localport=3002
netsh advfirewall firewall add rule name="CIRP Backend Port 3002 Out" dir=out action=allow protocol=TCP localport=3002
echo ✓ Firewall rules added
echo.

echo Step 2: Allowing Port 8001 in Windows Firewall (AI Service)...
netsh advfirewall firewall delete rule name="CIRP AI Port 8001"
netsh advfirewall firewall add rule name="CIRP AI Port 8001" dir=in action=allow protocol=TCP localport=8001
netsh advfirewall firewall add rule name="CIRP AI Port 8001 Out" dir=out action=allow protocol=TCP localport=8001
echo ✓ AI Service firewall rules added
echo.

echo Step 3: Allowing Node.js through firewall...
netsh advfirewall firewall delete rule name="Node.js Server"
netsh advfirewall firewall add rule name="Node.js Server" dir=in action=allow program="%ProgramFiles%\nodejs\node.exe" enable=yes
netsh advfirewall firewall add rule name="Node.js Server" dir=out action=allow program="%ProgramFiles%\nodejs\node.exe" enable=yes
echo ✓ Node.js allowed
echo.

echo Step 4: Checking current IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
echo Your PC IP: %IP%
echo.

echo Step 5: Testing if backend is running...
curl -s http://localhost:3002/health >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Backend is running on localhost
) else (
    echo ✗ Backend is NOT running! Start it with: cd backend ; node server.js
)
echo.

echo ==========================================
echo Network Configuration Complete!
echo ==========================================
echo.
echo IMPORTANT:
echo 1. Your PC IP address is: %IP%
echo 2. Update mobile app API to use this IP
echo 3. Make sure PC and phone are on SAME WiFi
echo.
echo Test from phone browser: http://%IP%:3002/health
echo.
pause
