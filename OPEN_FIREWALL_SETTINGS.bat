@echo off
echo ================================================
echo  OPENING WINDOWS FIREWALL SETTINGS
echo ================================================
echo.
echo This will open Windows Firewall settings.
echo.
echo WHAT TO DO:
echo.
echo 1. Click "Advanced settings" (left side)
echo 2. Click "Inbound Rules" (left side)
echo 3. Click "New Rule..." (right side)
echo 4. Select "Port" and click Next
echo 5. Select "TCP" and type "3000" in Specific local ports
echo 6. Click Next
echo 7. Select "Allow the connection" 
echo 8. Click Next
echo 9. Check all three boxes (Domain, Private, Public)
echo 10. Click Next
echo 11. Name: "CIRP Backend Port 3000"
echo 12. Click Finish
echo.
echo Opening firewall settings now...
echo.
pause

start firewall.cpl

echo.
echo After you finish, test on your phone browser:
echo http://192.168.8.60:3000/health
echo.
pause
