@echo off
echo Adding Windows Firewall rule for Django Backend (Port 8000)...
echo.
echo This requires Administrator privileges.
echo.

netsh advfirewall firewall add rule name="Django Backend - Port 8000" dir=in action=allow protocol=TCP localport=8000

echo.
echo Firewall rule added successfully!
echo You can now access the Django backend from your phone.
echo.
pause
