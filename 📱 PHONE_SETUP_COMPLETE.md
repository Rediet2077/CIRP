# 📱 CIRP Mobile App - Running on Your Phone

## ✅ Setup Complete!

Your phone **SM A107F (R9AN9139KVJ)** is now connected and the app is building!

---

## 📱 Current Configuration

### Your Phone:
- **Model:** SM A107F (Samsung Galaxy A10s)
- **Android:** 11 (API 30)
- **Device ID:** R9AN9139KVJ
- **Status:** ✅ Authorized and connected

### Network Configuration:
- **Your PC IP:** 192.168.0.160
- **Backend Port:** 3002
- **App will connect to:** http://192.168.0.160:3002/api

### Important: Both your phone and PC must be on the same WiFi network!

---

## ⏳ What's Happening Now

The app is currently building and will be installed on your phone automatically.

**Build Progress:**
1. [x] Phone connected and authorized
2. [x] API configuration updated to your PC IP
3. [⏳] Gradle building APK (3-5 minutes)
4. [ ] APK installation on phone
5. [ ] App launches on your phone

**You'll see the CIRP app icon appear on your phone when it's ready!**

---

## 🧪 Testing Steps (Once App Launches)

### Step 1: Login
```
Email: citizen@test.com
Password: Test@123
```

### Step 2: Create a Test Report
1. Tap "Report Issue" or "+" button
2. Select category (e.g., "Streetlight")
3. Enter title: "Test report from phone"
4. Enter description
5. Take a photo (optional)
6. Add location (allow location permission)
7. Submit

### Step 3: Verify on Admin Dashboard
1. Open browser on PC: http://localhost:3000
2. Login as: `electrical.services@cirp.com` / `Test@123`
3. Check reports list
4. ✅ You should see your test report!

---

## 🔧 Network Requirements

### CRITICAL: Same WiFi Network
**Your phone and PC MUST be on the same WiFi network!**

To verify:
1. **PC:** Run `ipconfig` → Look for IPv4 (192.168.0.160)
2. **Phone:** Settings → WiFi → Check connected network
3. **Both should show same network name (SSID)**

### If Connection Fails:
1. Check both devices on same WiFi
2. Verify PC firewall allows port 3002:
   ```powershell
   netsh advfirewall firewall add rule name="CIRP Backend" dir=in action=allow protocol=TCP localport=3002
   ```
3. Test backend is accessible:
   ```
   # From PC browser:
   http://192.168.0.160:3002/health
   
   # Should show: {"status":"ok",...}
   ```

---

## 📊 Backend Services Status

All services are running and accessible:

| Service | URL (from PC) | URL (from Phone) |
|---------|---------------|------------------|
| Backend API | http://localhost:3002 | http://192.168.0.160:3002 |
| Admin Dashboard | http://localhost:3000 | http://192.168.0.160:3000 |
| AI Service | http://localhost:8001 | http://192.168.0.160:8001 |

---

## 🔑 Test Accounts

### Mobile App (Citizen):
```
citizen@test.com / Test@123
redietsharew231@gmail.com / Test@123
```

### Admin Dashboard (PC Browser):
```
admin@cirp.com / Test@123 (System Admin)
public.works@cirp.com / Test@123
water.sewage@cirp.com / Test@123
sanitation@cirp.com / Test@123
electrical.services@cirp.com / Test@123
```

---

## 🎯 Full Test Flow

### End-to-End Integration Test:

1. **📱 Phone - Submit Report:**
   - Open CIRP app on your phone
   - Login as citizen
   - Create report: Category "Water Leakage"
   - Submit with photo and location

2. **🖥️ PC - Verify Backend:**
   - Check terminal logs for POST /api/reports
   - Should show: "Creating report with category_id..."
   - Should show: "Department ID: [water-sewage-id]"

3. **🌐 PC - Check Admin Dashboard:**
   - Open http://localhost:3000
   - Login as `water.sewage@cirp.com`
   - Navigate to Reports
   - ✅ New "Water Leakage" report appears!

4. **📱 Phone - Check Status:**
   - Go to "My Reports" in mobile app
   - See report status change when admin updates it

---

## 🐛 Troubleshooting

### App won't connect to backend:
```
Error: "Network error" or "Connection refused"
```
**Solution:**
1. Verify same WiFi network
2. Test from phone browser: http://192.168.0.160:3002/health
3. If fails, check PC firewall
4. Restart backend: `cd backend && npm start`

### Phone not authorized:
```
Error: "Device not authorized"
```
**Solution:**
1. Check your phone screen for USB debugging popup
2. Select "Always allow from this computer"
3. Run: `adb devices` (should show "device", not "unauthorized")

### Build fails:
```
Error: Gradle build failed
```
**Solution:**
```bash
cd mobile
flutter clean
flutter pub get
flutter run -d R9AN9139KVJ
```

### Wrong IP address:
If you change WiFi networks, update the IP:
1. Find new IP: `ipconfig`
2. Update `mobile/lib/core/constants/api_constants.dart`
3. Change `_physicalDeviceBaseUrl` to new IP
4. Rebuild: `flutter run -d R9AN9139KVJ`

---

## ⚡ Quick Commands

### Restart App on Phone:
```bash
cd mobile
flutter run -d R9AN9139KVJ
```

### Check Phone Connection:
```bash
adb devices
```

### View App Logs:
```bash
adb logcat | findstr "CIRP"
```

### Uninstall App:
```bash
flutter run -d R9AN9139KVJ --uninstall-only
```

### Reinstall Fresh:
```bash
cd mobile
flutter clean
flutter pub get
flutter run -d R9AN9139KVJ
```

---

## ✅ What's Next

Once the build completes (2-3 minutes):

1. ✅ CIRP app will appear on your phone
2. ✅ Tap to open
3. ✅ Login screen appears
4. ✅ Enter credentials and start testing!

**The app is building now... watch your phone screen!** 📱✨

---

## 📞 Need Help?

**Backend logs:** Check the terminal running `npm start` in backend folder

**Mobile logs:** Run `adb logcat` in another terminal

**Network test:** Open phone browser → http://192.168.0.160:3002/health

---

**Status:** ⏳ Building APK for your phone...
**ETA:** 2-3 minutes
**Device:** SM A107F (R9AN9139KVJ)
**Network:** 192.168.0.160:3002
