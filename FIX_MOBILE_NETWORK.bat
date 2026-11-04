@echo off
echo ============================================
echo  CIRP Mobile Network Fix
echo  Adding Windows Firewall Rule
echo ============================================
echo.

echo Creating firewall rule for Node.js backend...
netsh advfirewall firewall add rule name="CIRP Backend - Port 3000" dir=in action=allow protocol=TCP localport=3000
echo.

echo Testing network access...
curl -s http://192.168.8.60:3000/health
echo.

echo ============================================
echo  Done! Mobile app should now be able to
echo  connect to the backend.
echo ============================================
pause
