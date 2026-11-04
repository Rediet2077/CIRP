# 🚀 Next Steps - Getting Started with Your Backend

## ✅ What's Already Done

Your complete full-stack CIRP application is now ready with:
- ✅ Node.js Backend API (25+ endpoints)
- ✅ PostgreSQL Database Schema (10 tables)
- ✅ Mobile App (Flutter) - configured to connect
- ✅ Admin Dashboard (Next.js) - ready to connect
- ✅ Authentication & Authorization
- ✅ Sample data for testing

## 📋 Before You Start

Make sure you have:
1. **PostgreSQL** installed and running
   - Download: https://www.postgresql.org/download/windows/
   - Default username: `postgres`
   - Remember your password!

2. **Node.js** installed
   - Already installed ✅

## 🎯 Quick Start (3 Steps)

### Step 1: Setup Database (One-Time)

Open a new Command Prompt window:

```bash
cd C:\Users\Usuario\Documents\CIRP\backend
SETUP.bat
```

This will:
- Install all dependencies
- Create the PostgreSQL database
- Create all tables
- Add sample users and data

**Default password for PostgreSQL:** `postgres`
(If you set a different password during installation, edit `backend/.env` file)

### Step 2: Start the Backend Server

Double-click this file:
```
C:\Users\Usuario\Documents\CIRP\START_BACKEND.bat
```

Or run manually:
```bash
cd C:\Users\Usuario\Documents\CIRP\backend
npm start
```

You should see:
```
🚀 CIRP Backend Server Started!
📡 Server running on http://localhost:3000
```

### Step 3: Test It Works

Open your browser and go to:
```
http://localhost:3000
```

You should see the API information page!

## 🧪 Testing the API

### Test 1: Health Check
Open browser: http://localhost:3000/health

Should return:
```json
{
  "status": "ok",
  "timestamp": "2024-10-18T..."
}
```

### Test 2: Login
Use Postman, Thunder Client, or cURL:

```bash
curl -X POST http://localhost:3000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"citizen@test.com\",\"password\":\"Test@123\"}"
```

Should return a JWT token!

## 📱 Connecting Your Mobile App

### Option A: Testing on Web (Easiest)

Your mobile app at https://rediet2077.github.io/CIRP/ is configured for local storage.

To connect to the backend:
1. Backend must be running
2. Mobile app will auto-detect and use the API
3. Login: citizen@test.com / Test@123

### Option B: Testing on Physical Phone

1. **Find your PC's IP address:**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. **Edit mobile app configuration:**
   Open: `mobile\lib\core\constants\api_constants.dart`
   
   Change line 6:
   ```dart
   static const String _physicalDeviceBaseUrl = 'http://YOUR_IP_HERE:3000';
   ```

3. **Make sure phone and PC are on same WiFi**

4. **Rebuild the app:**
   ```bash
   cd mobile
   flutter build apk --release
   ```

5. **Install on phone:**
   APK location: `mobile\build\app\outputs\flutter-apk\app-release.apk`

## 🎯 Default Accounts

### Admin Account
- Email: `admin@cirp.com`
- Password: `Test@123`
- Can: Manage everything

### Test Citizen Account
- Email: `citizen@test.com`
- Password: `Test@123`
- Can: Create and manage own reports

## 📊 What You Can Do Now

1. **Create Reports** - Mobile app or API
2. **View Reports** - Mobile app or API
3. **Manage Users** - Admin endpoints
4. **Update Report Status** - Admin endpoints
5. **Add Comments** - Mobile app or API
6. **View Statistics** - Admin endpoints

## 📡 API Endpoints Quick Reference

Base URL: `http://localhost:3000/api`

**Authentication:**
- POST `/auth/login` - Login
- POST `/auth/register` - Register new user
- GET `/auth/me` - Get current user (needs token)

**Reports:**
- GET `/reports` - Get all reports
- POST `/reports` - Create report
- GET `/reports/:id` - Get single report
- PATCH `/reports/:id/status` - Update status (admin)
- POST `/reports/:id/comments` - Add comment

**Categories:**
- GET `/categories` - Get all categories

**Users (Admin):**
- GET `/users` - Get all users
- POST `/users` - Create user
- PUT `/users/:id` - Update user
- DELETE `/users/:id` - Delete user

## 🛠️ Troubleshooting

### Problem: SETUP.bat fails

**Check:**
1. PostgreSQL is running
2. Edit `backend\.env` and set your PostgreSQL password:
   ```env
   DB_PASSWORD=your_actual_password
   ```
3. Run `SETUP.bat` again

### Problem: Server won't start

**Solution:**
1. Check if port 3000 is already in use
2. Change port in `backend\.env`:
   ```env
   PORT=3001
   ```
3. Update mobile app to use new port

### Problem: Can't connect from phone

**Check:**
1. Backend is running (`http://localhost:3000/health` works on PC)
2. Phone and PC on same WiFi network
3. Windows Firewall allows connections on port 3000
4. Mobile app has correct IP address in `api_constants.dart`

## 📚 Documentation

- **Full Setup Guide:** `BACKEND_SETUP_GUIDE.md`
- **Complete Summary:** `FULL_STACK_SUMMARY.md`
- **Backend API Docs:** `backend/README.md`
- **Mobile App:** `mobile/README.md`

## 🎊 You're Ready!

Everything is set up and ready to use. Just run:

1. `START_BACKEND.bat` - Start the server
2. Open mobile app or test with Postman
3. Login and create reports!

**Need help?** Check the troubleshooting section or documentation files.

---

**🚀 Happy Coding!**
