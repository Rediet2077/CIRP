@echo off
echo Setting up ADB port forwarding...
adb -s R9AN9139KVJ reverse tcp:8000 tcp:8000
adb -s R9AN9139KVJ reverse tcp:8001 tcp:8001
echo Port forwarding setup complete!
echo Backend: localhost:8000 -> device localhost:8000
echo AI API: localhost:8001 -> device localhost:8001
pause
