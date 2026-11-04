# 🚀 CIRP Backend with SQLite - Quick Setup

## ✅ Why SQLite?

- **Zero Configuration** - No database installation needed!
- **Portable** - Database is just a file
- **Perfect for Development** - Fast and simple
- **Production Ready** - Great for small to medium apps

## ⚡ Super Quick Start (2 Steps!)

### Step 1: Setup Backend

Open Command Prompt in the CIRP folder:

```bash
cd C:\Users\Usuario\Documents\CIRP\backend
SETUP.bat
```

This will:
- Install Node.js dependencies
- Create the SQLite database automatically
- Create all tables and sample data

### Step 2: Start Server

```bash
START.bat
```

Or:
```bash
npm start
```

**That's it!** 🎉

Server running on: http://localhost:3000

No PostgreSQL, No MySQL, No installation required!

## 📦 What You Get

✅ **Complete REST API** - 25+ endpoints
✅ **SQLite Database** - Single file at `backend/database/cirp.db`
✅ **Sample Data** - 2 users, 6 categories, 3 reports
✅ **JWT Authentication** - Secure & working
✅ **All Features** - Reports, Comments, Users, etc.

## 🔐 Default Login

**Admin:**
- Email: admin@cirp.com
- Password: Test@123

**Test User:**
- Email: citizen@test.com
- Password: Test@123

## 🧪 Test It Works

**Health Check:**
```
http://localhost:3000/health
```

**Get Categories:**
```
http://localhost:3000/api/categories
```

**Login (get token):**
```bash
curl -X POST http://localhost:3000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"citizen@test.com\",\"password\":\"Test@123\"}"
```

## 📁 Database Location

Your database is stored at:
```
C:\Users\Usuario\Documents\CIRP\backend\database\cirp.db
```

You can:
- **Backup**: Just copy this file
- **Reset**: Delete the file and run `npm run init-db`
- **View**: Use DB Browser for SQLite (https://sqlitebrowser.org/)

## 🔧 Configuration

All settings in `backend\.env`:

```env
PORT=3000                     # Server port
DB_PATH=./database/cirp.db    # Database location
JWT_SECRET=your-secret-here   # JWT secret key
```

## 📱 Connect Mobile App

The mobile app is already configured to use `localhost:3000`.

**For physical phone:**
1. Find your PC's IP: `ipconfig`
2. Update `mobile\lib\core\constants\api_constants.dart`:
   ```dart
   static const String _physicalDeviceBaseUrl = 'http://YOUR_IP:3000';
   ```

## 🛠️ Common Commands

**Start server:**
```bash
npm start
```

**Start with auto-reload:**
```bash
npm run dev
```

**Reset database:**
```bash
npm run init-db
```

**View database:**
```bash
sqlite3 database/cirp.db
.tables
.schema users
SELECT * FROM users;
.quit
```

## 📊 Database Structure

10 Tables:
- users
- departments
- categories
- reports
- report_images
- comments
- report_activity
- notifications
- contractors
- audit_logs

## ✨ Features

✅ User registration & login
✅ JWT authentication
✅ Create & manage reports
✅ Add comments
✅ Upload images
✅ Status tracking
✅ Statistics
✅ Role-based access
✅ Activity logging
✅ Notifications

## 🚀 Advantages of SQLite

1. **No Installation** - Works immediately
2. **Portable** - Database is a single file
3. **Fast** - Great performance for single-user
4. **Reliable** - Used by millions of apps
5. **Simple** - Easy backup and restore
6. **Zero Config** - No server, no setup

## 🔄 Backup & Restore

**Backup:**
```bash
copy backend\database\cirp.db backend\database\cirp-backup.db
```

**Restore:**
```bash
copy backend\database\cirp-backup.db backend\database\cirp.db
```

## 📈 Scaling Up

SQLite is perfect for:
- Development
- Testing  
- Small to medium apps (< 100k users)
- Single-server deployments

Need to scale? Easy migration path to:
- PostgreSQL
- MySQL
- MariaDB

(Just update the database module, schema is compatible!)

## 🐛 Troubleshooting

**Port already in use?**
Change PORT in `.env` to 3001

**Database locked?**
Close any SQLite browser tools

**Can't connect from phone?**
Check Windows Firewall allows port 3000

## 🎉 You're Ready!

Everything works out of the box:
- ✅ Backend API running
- ✅ Database created
- ✅ Sample data loaded
- ✅ Mobile app can connect
- ✅ Admin dashboard can connect

**Start building! 🚀**

---

## 📝 API Endpoints

Base: `http://localhost:3000/api`

**Auth:**
- POST `/auth/register` - Register
- POST `/auth/login` - Login
- GET `/auth/me` - Get profile

**Reports:**
- GET `/reports` - List reports
- POST `/reports` - Create report
- GET `/reports/:id` - Get report
- PATCH `/reports/:id/status` - Update status

**Categories:**
- GET `/categories` - List categories

**Users (Admin):**
- GET `/users` - List users
- POST `/users` - Create user
- PUT `/users/:id` - Update user
- DELETE `/users/:id` - Delete user

---

**Need help?** The backend is fully functional and ready to use! 🎊
