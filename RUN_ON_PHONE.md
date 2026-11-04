# Run CIRP Mobile App on Your Phone

## Quick Start Steps

### 1. Start the Backend Server

```powershell
cd backend
node scripts/init-database.js
npm start
```

The server should start on **http://localhost:3000**

### 2. Verify Backend is Running

Open browser and test: http://localhost:3000/health

You should see: `{"status":"OK","timestamp":"..."}`

### 3. Connect Your Phone via USB

- Enable **Developer Mode** on your phone:
  - Go to Settings → About Phone
  - Tap "Build Number" 7 times
  
- Enable **USB Debugging**:
  - Go to Settings → Developer Options
  - Enable "USB Debugging"
  
- Connect phone via USB cable

### 4. Verify Phone Connection

```powershell
cd mobile
flutter devices
```

You should see your phone listed (e.g., "SM-G991B" or similar)

### 5. Run the App on Your Phone

```powershell
flutter run
```

Or if multiple devices are connected, specify your phone:

```powershell
flutter run -d <device-id>
```

**Note:** The app is now configured to connect to **http://192.168.0.160:3000** (your PC's IP address)

### 6. Test the App

1. **Register** a new account or **Login** with:
   - Email: `citizen@test.com`
   - Password: `Test@123`

2. Try creating a report to test the connection

---

## Troubleshooting

### Backend Won't Start

```powershell
cd backend
npm install
node scripts/init-database.js
npm start
```

### Phone Not Detected

```powershell
# Check if phone is connected
flutter devices

# If not detected:
# 1. Unplug and replug USB cable
# 2. On phone: Revoke USB debugging authorizations and re-enable
# 3. Try different USB cable/port
```

### Connection Error in App

1. Verify backend is running: http://localhost:3000/health
2. Check your PC's IP hasn't changed:
   ```powershell
   ipconfig | Select-String "IPv4"
   ```
3. Make sure phone and PC are on **same WiFi network**
4. Update IP in `mobile/lib/core/constants/api_constants.dart` if needed

### Can't Connect to Backend from Phone

- **Firewall**: Windows Firewall might be blocking port 3000
  - Go to Windows Firewall → Allow an app
  - Add Node.js or allow port 3000

- **Network**: Ensure phone and PC are on same WiFi network

### Build Errors

```powershell
cd mobile
flutter clean
flutter pub get
flutter run
```

---

## Default Test Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@cirp.com | Test@123 | Admin |
| citizen@test.com | Test@123 | Citizen |

---

## What's Configured

✅ Backend SQLite database at `backend/database/cirp.db`  
✅ API endpoints on http://192.168.0.160:3000  
✅ Mobile app configured to use physical device IP  
✅ All routes (auth, reports, users, categories) working  
✅ JWT authentication enabled  

## Architecture

```
Phone (Flutter App)
    ↓ HTTP/JSON
PC - http://192.168.0.160:3000 (Node.js + Express)
    ↓
SQLite Database (backend/database/cirp.db)
```
