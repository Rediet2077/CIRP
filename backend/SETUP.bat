@echo off
echo ========================================
echo  CIRP Backend Setup
echo ========================================
echo.

echo [1/3] Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo [2/3] Initializing database...
call npm run init-db
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    echo Make sure PostgreSQL is running and credentials in .env are correct
    pause
    exit /b 1
)
echo ✓ Database initialized
echo.

echo [3/3] Setup complete!
echo.
echo ========================================
echo  Ready to start!
echo ========================================
echo.
echo Run: npm start    (or npm run dev for development)
echo.
echo Default credentials:
echo   Admin: admin@cirp.com / Test@123
echo   User: citizen@test.com / Test@123
echo.
pause
