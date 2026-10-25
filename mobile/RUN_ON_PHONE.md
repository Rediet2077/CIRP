# CIRP Mobile App - Run on Your Phone

This guide will help you run the CIRP mobile app on your Android phone.

---

## Prerequisites

### ✅ What You Have
- ✅ Flutter installed (v3.44.8)
- ✅ Flutter project initialized
- ✅ Backend API running on `http://localhost:8000`
- ✅ AI Service running on `http://localhost:8001`

### 📱 What You Need
- Android phone (Android 5.0 or higher)
- USB cable to connect phone to PC
- USB Debugging enabled on your phone

---

## Step 1: Enable USB Debugging on Your Phone

### For Most Android Phones:

1. **Open Settings** on your phone
2. **Go to "About Phone"**
3. **Tap "Build Number" 7 times** (this enables Developer Options)
4. **Go back to Settings**
5. **Find "Developer Options"** (might be under System > Advanced)
6. **Enable "USB Debugging"**
7. **Connect your phone to PC with USB cable**
8. **Accept the debugging prompt** on your phone

---

## Step 2: Verify Phone Connection

Open PowerShell and run:

\`\`\`powershell
# Check if phone is connected
flutter devices
\`\`\`

You should see your phone listed. Example output:
\`\`\`
Found 2 connected devices:
  SM G950F (mobile) • 1234567890ABCDEF • android-arm64 • Android 11 (API 30)
  Chrome (web)     • chrome           • web-javascript • Google Chrome 120.0
\`\`\`

---

## Step 3: Configure API Endpoints

The mobile app needs to connect to your computer's backend API. Since your phone can't access `localhost`, you need to use your computer's IP address.

### Get Your Computer's IP Address:

\`\`\`powershell
# Get your local IP address
ipconfig | findstr /i "IPv4"
\`\`\`

Look for something like: `192.168.1.100` or `192.168.137.1`

### Update API Configuration:

Create a file at `mobile/lib/core/config/api_config.dart`:

\`\`\`dart
class ApiConfig {
  // Replace with your computer's IP address
  static const String baseUrl = 'http://192.168.1.100:8000';
  static const String aiServiceUrl = 'http://192.168.1.100:8001';
  
  // API Endpoints
  static const String apiVersion = '/api/v1';
  static const String loginEndpoint = '$apiVersion/auth/login/';
  static const String registerEndpoint = '$apiVersion/auth/register/';
  static const String reportsEndpoint = '$apiVersion/reports/';
  static const String categoriesEndpoint = '$apiVersion/categories/';
}
\`\`\`

**Important:** Replace `192.168.1.100` with YOUR computer's actual IP address!

---

## Step 4: Update Backend to Allow Phone Access

Your Django backend needs to accept connections from your phone's IP.

### Update Backend `.env`:

Open `backend/.env` and update:

\`\`\`env
# Allow connections from your local network
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,192.168.1.100

# Allow CORS from your phone
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://192.168.1.100:3000
\`\`\`

### Restart Backend:

\`\`\`powershell
# Stop the current backend (Ctrl+C)
# Then start it on all interfaces
cd backend
python manage.py runserver 0.0.0.0:8000
\`\`\`

### Update AI Service (if needed):

The AI service is already running on `0.0.0.0:8001`, so it should be accessible.

---

## Step 5: Run the App on Your Phone

### Option A: Using PowerShell

\`\`\`powershell
# Navigate to mobile folder
cd c:\Users\Usuario\Documents\CIRP\mobile

# Run the app
flutter run
\`\`\`

### Option B: Using Hot Reload (Recommended for Development)

\`\`\`powershell
cd c:\Users\Usuario\Documents\CIRP\mobile
flutter run --hot
\`\`\`

Flutter will:
1. Build the app
2. Install it on your phone
3. Launch it automatically
4. Enable hot reload (press 'r' to reload, 'R' to hot restart)

---

## Step 6: Test the Connection

Once the app is running on your phone:

1. **Check Network Connection**: Make sure your phone and computer are on the same Wi-Fi network
2. **Test Backend**: The app should be able to fetch categories and reports
3. **Test Login**: Try logging in with test credentials

### Troubleshooting Connection:

If the app can't connect to the backend:

\`\`\`powershell
# Test if your phone can reach your computer
# On your phone, open a browser and visit:
http://192.168.1.100:8000/

# You should see the CIRP API welcome page
\`\`\`

---

## Common Commands

### Check Connected Devices
\`\`\`powershell
flutter devices
\`\`\`

### Run on Specific Device
\`\`\`powershell
flutter run -d <device-id>
\`\`\`

### Build APK (for installation without cable)
\`\`\`powershell
flutter build apk --release
\`\`\`
The APK will be at: `build/app/outputs/flutter-apk/app-release.apk`

### Install APK on Phone
\`\`\`powershell
flutter install
\`\`\`

### View Logs
\`\`\`powershell
flutter logs
\`\`\`

### Clear Cache and Rebuild
\`\`\`powershell
flutter clean
flutter pub get
flutter run
\`\`\`

---

## Firewall Settings (Windows)

If your phone can't connect, you may need to allow incoming connections:

### Allow Backend Through Firewall:

1. **Open Windows Defender Firewall**
2. **Click "Allow an app through firewall"**
3. **Find "Python"** (for Django backend)
4. **Check both "Private" and "Public" networks**
5. **Click OK**

Or use PowerShell:

\`\`\`powershell
# Allow Python through firewall
netsh advfirewall firewall add rule name="Django Backend" dir=in action=allow protocol=TCP localport=8000

# Allow AI Service through firewall
netsh advfirewall firewall add rule name="CIRP AI Service" dir=in action=allow protocol=TCP localport=8001
\`\`\`

---

## Network Configuration Summary

| Service | Computer Address | Phone Access |
|---------|-----------------|--------------|
| Backend API | localhost:8000 | 192.168.1.100:8000 |
| AI Service | localhost:8001 | 192.168.1.100:8001 |
| Admin Dashboard | localhost:3000 | 192.168.1.100:3000 |

**Remember:** Replace `192.168.1.100` with your actual computer IP!

---

## Development Workflow

### Hot Reload Workflow:

1. Make changes to your code
2. Press **'r'** in the terminal to hot reload
3. Press **'R'** to hot restart
4. Press **'q'** to quit

### Best Practices:

- Keep the app running with `flutter run --hot` during development
- Use hot reload ('r') for UI changes
- Use hot restart ('R') for state changes
- Test on real device for camera, GPS, and other hardware features

---

## Troubleshooting

### Problem: "No devices found"
**Solution:**
- Check USB cable connection
- Enable USB Debugging on phone
- Accept debugging prompt on phone
- Try different USB port
- Run: `adb devices` to check connection

### Problem: "App can't connect to API"
**Solution:**
- Check if phone and computer are on same Wi-Fi
- Verify computer's IP address: `ipconfig`
- Test URL in phone browser: `http://YOUR_IP:8000/`
- Check firewall settings
- Restart backend with: `python manage.py runserver 0.0.0.0:8000`

### Problem: "Build failed"
**Solution:**
- Run: `flutter clean`
- Run: `flutter pub get`
- Check Android SDK installation
- Update Flutter: `flutter upgrade`

### Problem: "Permission denied"
**Solution:**
- Check app has required permissions in `AndroidManifest.xml`
- Grant permissions manually in phone settings

---

## Quick Start Command

After setting everything up, use this single command:

\`\`\`powershell
cd c:\Users\Usuario\Documents\CIRP\mobile && flutter run --hot
\`\`\`

---

## Building for Production

### Build Release APK:

\`\`\`powershell
cd c:\Users\Usuario\Documents\CIRP\mobile
flutter build apk --release --target-platform android-arm64
\`\`\`

### Build App Bundle (for Play Store):

\`\`\`powershell
flutter build appbundle --release
\`\`\`

### Install Release APK:

1. Copy APK from `build/app/outputs/flutter-apk/app-release.apk`
2. Transfer to phone (via USB, email, or file sharing)
3. Enable "Install from Unknown Sources" on phone
4. Tap the APK file to install

---

## Next Steps

1. ✅ **Connect your phone** via USB
2. ✅ **Enable USB debugging**
3. ✅ **Get your computer's IP address**
4. ✅ **Update API configuration**
5. ✅ **Restart backend** on `0.0.0.0:8000`
6. ✅ **Run `flutter run`**
7. ✅ **Start developing!**

---

**Need help? Check the logs with `flutter logs` or ask for assistance!** 📱✨
