@echo off
title CIRP Backend Server
color 0A
echo.
echo ========================================
echo    CIRP Backend Server
echo ========================================
echo.
echo Starting server on http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.
cd backend
call npm start
