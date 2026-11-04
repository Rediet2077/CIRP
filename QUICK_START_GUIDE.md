# 🚀 CIRP Platform - Quick Start Guide

## ⚡ Fastest Way to Start

**Double-click this file:**
```
RESTART_ALL_FRESH.bat
```

Wait 10 seconds, then open in browser:
- Admin Dashboard: http://localhost:3001
- Backend API: http://localhost:3000

---

## 📋 What's Running?

After starting, you'll have 3 terminal windows:

1. **CIRP Backend** (Port 3000)
   - Node.js + Express + SQLite
   - REST API for all operations

2. **CIRP AI Service** (Port 8001)
   - FastAPI + Python
   - Image classification & duplicate detection

3. **CIRP Admin Dashboard** (Port 3001)
   - Next.js + React
   - Web interface for admins

---

## 🔑 Login Credentials

### Admin Account:
```
Email: admin@cirp.com
Password: Test@123
```

### Test Citizen:
```
Email: citizen@test.com
Password: Test@123
```

---

## ✅ What's Fixed (All Issues Resolved)

1. ✅ Hydration warnings - Fixed
2. ✅ HTTP 404 errors - Fixed
3. ✅ API connection - Working
4. ✅ Database - Initialized with data
5. ✅ Ports - Configured correctly

---

## 🧪 Verify It's Working

### Test Backend:
```bash
curl http://localhost:3000/health
```
Should return: `{"status":"ok",...}`

### Test Categories:
```bash
curl http://localhost:3000/api/categories
```
Should return: 12 categories

### Or use verification script:
```bash
VERIFY_FIX.bat
```

---

## 🛑 Stop All Services

Press `Ctrl + C` in each terminal window

Or:
```bash
taskkill /F /IM node.exe
```

---

## 🔄 Restart Individual Services

### Backend Only:
```bash
cd backend
npm start
```

### Admin Dashboard Only:
```bash
cd "admin page"
npm run dev
```

### AI Service Only:
```bash
cd ai
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## 📚 Full Documentation

- `🎉 ALL_ISSUES_FIXED.md` - Complete summary of all fixes
- `✅ HYDRATION_FIXED.md` - Hydration error details
- `✅ API_404_FIXED.md` - API 404 error details
- `SQLITE_BACKEND_GUIDE.md` - Backend setup guide

---

## 🎯 Service URLs Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Admin Dashboard | http://localhost:3001 | Web interface |
| Backend API | http://localhost:3000 | REST API |
| Backend Health | http://localhost:3000/health | Status check |
| AI Service | http://localhost:8001 | AI endpoints |
| AI Docs | http://localhost:8001/docs | API documentation |

---

## 💾 Database Location

```
C:\Users\Usuario\Documents\CIRP\backend\database\cirp.db
```

Contains:
- 12 categories
- 4 departments
- 2 test users
- All tables configured

---

## ⚠️ Common Issues

### Port already in use?
```bash
# Kill all Node.js processes
taskkill /F /IM node.exe

# Or change port in backend/.env
PORT=3002
```

### Database empty?
```bash
cd backend
npm run init-db
```

### Admin dashboard errors?
```bash
cd "admin page"
rm -rf node_modules
npm install
npm run dev
```

---

## ✨ You're Ready!

Everything is configured and working. Just run:
```
RESTART_ALL_FRESH.bat
```

Then open: **http://localhost:3001**

**Happy coding! 🎉**
