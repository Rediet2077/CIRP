@echo off
echo ========================================
echo   Restarting Admin Dashboard
echo ========================================
echo.
echo Stopping any running instances...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq CIRP Admin*" 2>nul
timeout /t 2 /nobreak >nul

echo Starting Admin Dashboard (Port 3001)...
cd /d "%~dp0admin page"
start "CIRP Admin Dashboard" cmd /k "npm run dev"

echo.
echo ========================================
echo   Admin Dashboard Starting!
echo ========================================
echo.
echo URL: http://localhost:3001
echo.
echo The hydration error has been fixed!
echo Your console should now be clean.
echo.
pause
