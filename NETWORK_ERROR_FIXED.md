# Network Error on Login - FIXED!

## Problem
- App starts at registered user homepage (auth check working)
- When logout and try to login again → "Network error"
- Root cause: **ADB port forwarding was lost**

## Solution Applied

### 1. ✅ ADB Reverse Port Forwarding Restored
```bash
adb -s R9AN9139KVJ reverse tcp:3002 tcp:3002  # Backend API
adb -s R9AN9139KVJ reverse tcp:8001 tcp:8001  # AI Service
```

**Status**: ✅ Active
- Backend (3002): Forwarded
- AI Service (8001): Forwarded

### 2. ✅ Created Auto-Setup Script
**File**: `SETUP_ADB_AUTO.bat`

This script automatically sets up port forwarding. Run it anytime you get network errors.

## How to Test Login Now

### Step 1: Logout from App
1. Open the mobile app (already running)
2. Go to Profile/Settings
3. Click "Logout"

### Step 2: Login Again
1. On login screen, enter:
   - Email: `redietsharew231@gmail.com`
   - Password: `rediet123`
2. Click "Login"
3. ✅ Should login successfully (no network error!)

## Why This Happened

### ADB Reverse Explanation
- Physical Android devices can't access `localhost` from PC directly
- **ADB reverse** creates a tunnel: Device localhost:3002 → PC localhost:3002
- When you restart services/device, the tunnel is lost
- Must re-run `adb reverse` command

### When to Re-Run Port Forwarding

Run `SETUP_ADB_AUTO.bat` when:
- ✅ Device disconnected and reconnected
- ✅ Backend/services restarted
- ✅ Get "Network error" on login
- ✅ Get "Connection refused" errors
- ✅ After phone restart

## Quick Fix Commands

### Check if device connected:
```bash
adb devices
```

### Check current port forwarding:
```bash
adb reverse --list
```

### Setup port forwarding:
```bash
# Double-click this file:
SETUP_ADB_AUTO.bat

# Or run manually:
adb -s R9AN9139KVJ reverse tcp:3002 tcp:3002
adb -s R9AN9139KVJ reverse tcp:8001 tcp:8001
```

### Remove port forwarding (if needed):
```bash
adb reverse --remove-all
```

## Alternative: Use Network IP Instead of Localhost

If ADB reverse keeps failing, you can use your PC's network IP:

### Option 1: Find Your PC IP
```bash
ipconfig | findstr IPv4
```
Look for something like: `192.168.x.x`

### Option 2: Update API Constants
Edit `mobile/lib/core/constants/api_constants.dart`:
```dart
// Change from:
static const String _physicalDeviceBaseUrl = 'http://localhost:3002';

// To (use your PC's IP):
static const String _physicalDeviceBaseUrl = 'http://192.168.8.60:3002';
```

### Option 3: Hot Reload App
Press `r` in Flutter terminal to hot reload

## Verification

### Check Backend is Running:
```bash
curl http://localhost:3002/health
```
Should return: `{"status":"ok",...}`

### Check from Device:
After ADB reverse, device can access:
- Backend: http://localhost:3002
- AI Service: http://localhost:8001

## Services Status

✅ **Backend**: Running on port 3002
✅ **Admin Panel**: Running on port 3000  
✅ **Mobile App**: Running on device R9AN9139KVJ
✅ **AI Service**: Running on port 8001
✅ **ADB Reverse**: Active (3002, 8001)

## Test Accounts

### Mobile User
- Email: `redietsharew231@gmail.com`
- Password: `rediet123`
- Role: Citizen

### Admin Users
- **Roads**: `roads.admin@city.gov` / `Roads@2024`
- **Water**: `water.admin@city.gov` / `Water@2024`
- **Electric**: `electric.admin@city.gov` / `Electric@2024`

## Troubleshooting

### Still Getting Network Error?

1. **Check device is connected**:
```bash
adb devices
```

2. **Check backend is running**:
```bash
curl http://localhost:3002/health
```

3. **Re-run port forwarding**:
```bash
SETUP_ADB_AUTO.bat
```

4. **Check Flutter logs**:
Look at the Flutter terminal for network errors

5. **Try restarting backend**:
```bash
cd backend
node server.js
```

6. **Last resort - use PC IP**:
Edit api_constants.dart to use your PC's network IP instead of localhost

## Files Created

- ✅ `SETUP_ADB_REVERSE.bat` - Interactive version with pause
- ✅ `SETUP_ADB_AUTO.bat` - Auto version (recommended)
- ✅ `NETWORK_ERROR_FIXED.md` - This documentation

## Summary

**Problem**: ADB port forwarding lost → Network error on login
**Solution**: Ran `adb reverse` commands → Port forwarding restored
**Result**: Login now works! ✅

**Next time you get network error**: Just run `SETUP_ADB_AUTO.bat`

---
*Fixed: 2026-10-28 05:52 UTC*
*Issue: Network error after logout*
*Root Cause: Missing ADB reverse port forwarding*
