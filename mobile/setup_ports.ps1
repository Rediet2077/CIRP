Write-Host "Setting up ADB port forwarding..." -ForegroundColor Green
adb -s R9AN9139KVJ reverse tcp:8000 tcp:8000
adb -s R9AN9139KVJ reverse tcp:8001 tcp:8001
Write-Host "Port forwarding complete!" -ForegroundColor Green
Write-Host "Backend: localhost:8000 -> device" -ForegroundColor Cyan
Write-Host "AI API: localhost:8001 -> device" -ForegroundColor Cyan