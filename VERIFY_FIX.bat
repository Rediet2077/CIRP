@echo off
echo ========================================
echo   Verifying CIRP Fixes
echo ========================================
echo.

echo [TEST 1] Backend Health Check...
curl -s http://localhost:3000/health
echo.
echo.

echo [TEST 2] Root Endpoint...
curl -s http://localhost:3000/
echo.
echo.

echo [TEST 3] Categories Endpoint (Should show 12 categories)...
curl -s http://localhost:3000/api/categories
echo.
echo.

echo [TEST 4] Check Admin Dashboard .env...
type "admin page\.env.local"
echo.
echo.

echo ========================================
echo   Verification Complete
echo ========================================
echo.
echo Expected Results:
echo - Health check should return "status":"ok"
echo - Categories should return array with 12 items
echo - .env should show http://localhost:3000/api
echo.
echo If backend is not running, use RESTART_ALL_FRESH.bat
echo.
pause
