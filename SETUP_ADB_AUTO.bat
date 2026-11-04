@echo off
echo Setting up ADB reverse port forwarding...
adb -s R9AN9139KVJ reverse tcp:3002 tcp:3002
adb -s R9AN9139KVJ reverse tcp:8001 tcp:8001
echo Port forwarding setup complete!
adb -s R9AN9139KVJ reverse --list
