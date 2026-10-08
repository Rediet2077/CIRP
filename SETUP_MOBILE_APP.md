# 📱 Quick Guide: Run CIRP Mobile App on Your Phone

Follow these simple steps to run the mobile app on your Android phone.

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Get Your Computer's IP Address

Open PowerShell and run:
\`\`\`powershell
ipconfig | findstr /i "IPv4"
\`\`\`

**Write down the IP address** (e.g., `192.168.1.100`)

---

### Step 2: Update API Configuration

1. Open: `mobile\lib\core\config\api_config.dart`
2. Find this line:
   \`\`\`dart
   static const String computerIp = '192.168.1.100'; // CHANGE THIS!
   \`\`\`
3. Replace `192.168.1.100` with YOUR computer's IP address
4. Save the file

---

### Step 3: Restart Backend on Network

Stop your current backend (Ctrl+C) and restart it:

\`\`\`powershell
cd c:\Users\Usuario\Documents\CIRP\backend
python manage.py runserver 0.0.0.0:8000
\`\`\`

This allows your phone to access the backend.

---

### Step 4: Enable USB Debugging on Phone

1. Go to **Settings > About Phone**
2. Tap **Build Number** 7 times (enables Developer Options)
3. Go back to **Settings > Developer Options**
4. Enable **USB Debugging**
5. Connect phone to PC with USB cable
6. Accept the debugging prompt on your phone

---

### Step 5: Run the App

**Option A - Use the Quick Start Script:**

Just double-click: `mobile\QUICK_START.bat`

**Option B - Manual Command:**

\`\`\`powershell
cd c:\Users\Usuario\Documents\CIRP\mobile
flutter run --hot
\`\`\`

---

## ✅ Verification

### Check Phone Connection:
\`\`\`powershell
flutter devices
\`\`\`
You should see your phone listed.

### Test Backend Access:
On your phone's browser, visit:
\`\`\`
http://YOUR_IP:8000/
\`\`\`
You should see the CIRP API welcome page.

---

## 🔥 Hot Reload Commands

While the app is running:
- Press **'r'** - Quick reload (for UI changes)
- Press **'R'** - Full restart (for code changes)
- Press **'h'** - Help
- Press **'q'** - Quit

---

## 🐛 Troubleshooting

### Problem: "No devices found"
- Check USB cable
- Enable USB Debugging
- Accept prompt on phone
- Try: `adb devices`

### Problem: "Can't connect to API"
- Make sure phone and PC are on same Wi-Fi
- Check your IP address is correct in `api_config.dart`
- Test backend URL in phone browser
- Restart backend on `0.0.0.0:8000`

### Problem: "Build failed"
\`\`\`powershell
cd mobile
flutter clean
flutter pub get
flutter run
\`\`\`

---

## 📦 Build APK for Installation

To create an APK file you can install directly:

\`\`\`powershell
cd mobile
flutter build apk --release
\`\`\`

APK location: `mobile\build\app\outputs\flutter-apk\app-release.apk`

Transfer this file to your phone and install it!

---

## 🎯 Summary

1. **Get IP**: `ipconfig | findstr /i "IPv4"`
2. **Update Config**: Edit `mobile\lib\core\config\api_config.dart`
3. **Restart Backend**: `python manage.py runserver 0.0.0.0:8000`
4. **Connect Phone**: Enable USB debugging, connect cable
5. **Run App**: Double-click `QUICK_START.bat` or `flutter run --hot`

---

**For detailed instructions, see: `mobile\RUN_ON_PHONE.md`**

🎉 **Ready to go! Your app should now be running on your phone!**
