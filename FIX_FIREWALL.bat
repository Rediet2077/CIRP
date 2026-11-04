@echo off
echo ========================================
echo   Adding Firewall Rule for CIRP Backend
echo ========================================
echo.
echo This will allow incoming connections on port 3002
echo.

netsh advfirewall firewall add rule name="CIRP Backend Port 3002" dir=in action=allow protocol=TCP localport=3002

echo.
echo Firewall rule added!
echo.
echo Now checking if the rule was created...
netsh advfirewall firewall show rule name="CIRP Backend Port 3002"
echo.
echo Done!
pause
