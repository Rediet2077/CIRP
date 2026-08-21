@echo off
color 0A
echo.
echo  ========================================
echo     CIRP - Community Infrastructure
echo       Reporting Platform
echo  ========================================
echo.
echo  How do you want to run the project?
echo.
echo  [1] Docker (Easiest - Recommended)
echo      - One command starts everything
echo      - No manual setup needed
echo      - Requires Docker Desktop
echo.
echo  [2] Manual Setup (All services separately)
echo      - More control
echo      - Can debug individual services
echo      - Requires PostgreSQL, Python, Node.js
echo.
echo  [3] Setup Only (First time setup)
echo      - Install dependencies
echo      - Configure environment
echo      - Create database
echo.
echo  [4] View Documentation
echo.
echo  [Q] Quit
echo.
echo  ========================================
echo.

set /p choice="Enter your choice (1-4 or Q): "

if "%choice%"=="1" goto docker
if "%choice%"=="2" goto manual
if "%choice%"=="3" goto setup
if "%choice%"=="4" goto docs
if "%choice%"=="Q" goto end
if "%choice%"=="q" goto end

echo Invalid choice!
pause
goto end

:docker
cls
echo ==========================================
echo Starting with Docker...
echo ==========================================
echo.
call START_DOCKER.bat
goto end

:manual
cls
echo ==========================================
echo Starting Manually...
echo ==========================================
echo.
echo IMPORTANT: Make sure you have:
echo  - PostgreSQL running with PostGIS
echo  - Python virtual environments set up
echo  - Node.js dependencies installed
echo.
echo If this is your first time, choose option 3 first!
echo.
pause
call START_ALL_MANUAL.bat
goto end

:setup
cls
echo ==========================================
echo First Time Setup
echo ==========================================
echo.
echo What would you like to set up?
echo.
echo [1] Backend (Django + Database)
echo [2] AI Service (FastAPI)
echo [3] Frontend (Next.js Admin Page)
echo [4] All of the above
echo [B] Back to main menu
echo.
set /p setup_choice="Enter your choice: "

if "%setup_choice%"=="1" (
    call SETUP_BACKEND.bat
)
if "%setup_choice%"=="2" (
    call SETUP_AI.bat
)
if "%setup_choice%"=="3" (
    call SETUP_FRONTEND.bat
)
if "%setup_choice%"=="4" (
    echo Setting up Backend...
    call SETUP_BACKEND.bat
    echo.
    echo Setting up AI Service...
    call SETUP_AI.bat
    echo.
    echo Setting up Frontend...
    call SETUP_FRONTEND.bat
)
if "%setup_choice%"=="B" goto start
if "%setup_choice%"=="b" goto start
goto end

:docs
cls
echo ==========================================
echo Documentation
echo ==========================================
echo.
echo Opening RUN_PROJECT.md...
start RUN_PROJECT.md
echo.
echo Other documentation files:
echo  - README.md (Main documentation)
echo  - SETUP_GUIDE.md (Detailed setup)
echo  - API_INTEGRATION.md (API details)
echo  - INTEGRATION_SUMMARY.md (Project summary)
echo.
pause
goto end

:end
echo.
echo Thank you for using CIRP!
echo.
pause
