# 🔧 Network Connection Fix - Registration Error

## ❌ Problem
Mobile app shows "**Network error**" when trying to register because:
- PC IP address is: `192.168.0.160`
- Mobile app was configured for: `192.168.8.60` ❌
- Firewall may be blocking port 3002

## ✅ Solution Applied

### 1. Updated Mobile App IP Address
**File**: `mobile/lib/core/constants/api_constants.dart`
```dart
// Changed from:
'http://192.168.8.60:3002'  ❌
// To:
'http://192.168.0.160:3002' ✅
```

### 2. Run Firewall Fix (REQUIRED)
**You must run this as Administrator:**

1. Find file: `C:\Users\Usuario\Documents\CIRP\FIX_NETWORK.bat`
2. **Right-click** → **Run as Administrator**
3. Wait for it to complete
4. Check output shows: ✓ Firewall rules added

**What it does:**
- Allows port 3002 (Backend)
- Allows port 8001 (AI Service)
- Allows Node.js through firewall
- Shows your current IP address

### 3. Restart Mobile App
After fixing firewall and IP:
```bash
cd mobile
flutter run -d R9AN9139KVJ
```

---

## 🧪 Test Steps

### Step 1: Test Backend is Reachable
**On your phone's browser**, go to:
```
http://192.168.0.160:3002/health
```

**Expected**: Should show JSON response like:
```json
{
  "status": "ok",
  "database": "connected"
}
```

**If it doesn't work:**
- ❌ PC and phone NOT on same WiFi
- ❌ Firewall still blocking
- ❌ Backend not running

### Step 2: Test Registration in App
1. Open CIRP mobile app
2. Click "Register"
3. Fill in:
   - Email: `test123@gmail.com`
   - Password: `Test@123`
   - Full Name: `Test User`
   - Phone: `+251912345678`
4. Click "Register"

**Expected**: Should go to OTP screen without "Network error"

**If still shows network error:**
- Check phone browser can reach: `http://192.168.0.160:3002/health`
- Check both on same WiFi network
- Run `FIX_NETWORK.bat` as Administrator again

---

## 🔍 Troubleshooting

### Problem: Phone browser can't reach backend
**Solutions:**
1. **Check same WiFi**: PC and phone must be on SAME WiFi network
2. **Check IP didn't change**: Run `ipconfig` on PC, verify IP is still `192.168.0.160`
3. **Check firewall**: Run `FIX_NETWORK.bat` as Administrator
4. **Check backend running**: Should see "Server running on http://localhost:3002"

### Problem: IP Address Keeps Changing
If your PC IP keeps changing (DHCP), you have 2 options:

**Option A: Set Static IP** (Recommended)
1. Open Network Settings
2. Change adapter properties
3. IPv4 Properties → Use the following IP
4. Set IP: `192.168.0.160`
5. Subnet: `255.255.255.0`
6. Gateway: `192.168.0.1`

**Option B: Update Mobile App Each Time**
1. Check PC IP: `ipconfig`
2. Update `api_constants.dart` with new IP
3. Restart mobile app

### Problem: Still Getting Network Error
**Last resort - USB ADB Reverse:**
```bash
# On PC
adb -s R9AN9139KVJ reverse tcp:3002 tcp:3002

# Then in mobile app, change to:
'http://localhost:3002'  # Instead of IP address
```

---

## 📊 Current Configuration

| Service | IP | Port | Status |
|---------|----|----|--------|
| **Backend** | 192.168.0.160 | 3002 | ✅ Running |
| **Admin** | localhost | 3000 | ✅ Running |
| **AI Service** | localhost | 8001 | ✅ Running |
| **Mobile App** | (device) | - | ⚠️ Needs restart |

**Mobile App API**: `http://192.168.0.160:3002`

---

## ✅ Quick Fix Checklist

- [ ] Run `FIX_NETWORK.bat` as Administrator
- [ ] Verify PC IP is `192.168.0.160` (run `ipconfig`)
- [ ] Test backend in phone browser: `http://192.168.0.160:3002/health`
- [ ] Restart mobile app: `flutter run -d R9AN9139KVJ`
- [ ] Try registration again in app

---

**After completing these steps, registration should work!** ✅

The backend logs already show OTP emails being sent successfully, so the backend is working. The issue is just network connectivity between phone and PC.
