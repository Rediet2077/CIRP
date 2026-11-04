@echo off
echo ========================================
echo   Testing CIRP Backend
echo ========================================
echo.

echo [1] Testing Health Endpoint...
curl -s http://localhost:3000/health
echo.
echo.

echo [2] Testing Root Endpoint...
curl -s http://localhost:3000/
echo.
echo.

echo [3] Testing Categories...
curl -s http://localhost:3000/api/categories
echo.
echo.

echo [4] Testing Auth Login...
curl -s -X POST http://localhost:3000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@cirp.com\",\"password\":\"Test@123\"}"
echo.
echo.

echo ========================================
echo   Testing Complete
echo ========================================
pause
