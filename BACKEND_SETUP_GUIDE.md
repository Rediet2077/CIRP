# 🚀 CIRP Backend Setup Guide

Complete guide to set up the Node.js backend with PostgreSQL database.

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Node.js** (v16 or higher)
   - Download: https://nodejs.org/
   - Verify: `node --version`

2. **PostgreSQL** (v13 or higher)
   - Download: https://www.postgresql.org/download/windows/
   - Or use Docker (see below)

3. **npm** or **yarn** (comes with Node.js)
   - Verify: `npm --version`

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install PostgreSQL

**Option A: Download Installer** (Recommended for Windows)
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer
3. Remember the password you set for `postgres` user
4. Keep default port: `5432`

**Option B: Use Docker** (If you have Docker installed)
```bash
docker run --name cirp-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15
```

### Step 2: Setup Backend

Open Command Prompt or PowerShell:

```bash
cd C:\Users\Usuario\Documents\CIRP\backend
```

**Run the setup script:**
```bash
SETUP.bat
```

This will:
- Install Node.js dependencies
- Create the database
- Create all tables
- Add sample data

### Step 3: Start the Server

```bash
START.bat
```

Or manually:
```bash
npm start
```

✅ **Done!** Server running on http://localhost:3000

---

## 🔧 Manual Setup (Detailed)

If the automatic setup doesn't work:

### 1. Configure Environment Variables

Edit `backend/.env`:

```env
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cirp_db
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD_HERE
JWT_SECRET=cirp-super-secret-key-2024
```

⚠️ **Important:** Change `DB_PASSWORD` to match your PostgreSQL password!

### 2. Install Dependencies

```bash
cd backend
npm install
```

### 3. Initialize Database

```bash
npm run init-db
```

This creates:
- ✅ Database: `cirp_db`
- ✅ 10 tables with relationships
- ✅ Default admin and test users
- ✅ Sample categories and departments
- ✅ 3 example reports

### 4. Start Server

**Development (with auto-reload):**
```bash
npm run dev
```

**Production:**
```bash
npm start
```

---

## 🔐 Default Credentials

After setup, use these credentials:

### Admin Account
- **Email:** admin@cirp.com
- **Password:** Test@123
- **Access:** Full system access

### Test Citizen Account
- **Email:** citizen@test.com
- **Password:** Test@123
- **Access:** Can create and manage own reports

---

## 📡 API Endpoints

Base URL: `http://localhost:3000/api`

### Health Check
```
GET /health
```

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user (requires token)

### Reports
- `GET /reports` - Get all reports
- `POST /reports` - Create report
- `GET /reports/:id` - Get single report
- `PATCH /reports/:id/status` - Update status
- `DELETE /reports/:id` - Delete report

### Categories
- `GET /categories` - Get all categories

### Users (Admin only)
- `GET /users` - Get all users
- `POST /users` - Create user
- `PUT /users/:id` - Update user
- `DELETE /users/:id` - Delete user

---

## 🧪 Testing the API

### Using cURL:

**1. Login:**
```bash
curl -X POST http://localhost:3000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"citizen@test.com\",\"password\":\"Test@123\"}"
```

**2. Get Reports (with token):**
```bash
curl http://localhost:3000/api/reports ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Browser:

Visit: http://localhost:3000

You'll see the API info page.

### Using Postman/Thunder Client:

1. Import the API base URL: `http://localhost:3000/api`
2. Test endpoints with proper headers

---

## 📱 Connecting Mobile App

### For Web (Browser):
No changes needed - already configured for `localhost:3000`

### For Physical Phone:

1. **Find your computer's IP address:**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. **Update mobile app:**
   
   Edit `mobile/lib/core/constants/api_constants.dart`:
   ```dart
   static const String _physicalDeviceBaseUrl = 'http://YOUR_IP:3000';
   static const String baseUrl = _physicalDeviceBaseUrl;
   ```

3. **Ensure phone and PC are on same WiFi network**

4. **Rebuild mobile app:**
   ```bash
   cd mobile
   flutter build apk --release
   ```

---

## 🗄️ Database Structure

The backend includes these tables:

| Table | Description |
|-------|-------------|
| users | User accounts with roles |
| departments | Government departments |
| categories | Report categories (Road, Water, etc.) |
| reports | Community issue reports |
| report_images | Images attached to reports |
| comments | Comments on reports |
| report_activity | Activity/audit log |
| notifications | User notifications |
| contractors | Contractor information |
| audit_logs | System audit trail |

---

## 🛠️ Troubleshooting

### Problem: "Database connection failed"

**Solution:**
1. Check if PostgreSQL is running:
   - Windows: Open Services → Look for "postgresql-x64-XX"
   - Or: Check Task Manager → Services

2. Verify credentials in `.env`:
   - DB_PASSWORD matches your PostgreSQL password
   - DB_USER is `postgres`
   - DB_PORT is `5432`

3. Test connection:
   ```bash
   psql -U postgres -h localhost
   ```

### Problem: "Port 3000 already in use"

**Solution:**
1. Change port in `.env`:
   ```env
   PORT=3001
   ```
2. Or find and stop the process using port 3000:
   ```bash
   netstat -ano | findstr :3000
   taskkill /PID <PID_NUMBER> /F
   ```

### Problem: "npm install fails"

**Solution:**
1. Clear npm cache:
   ```bash
   npm cache clean --force
   ```
2. Delete `node_modules`:
   ```bash
   rmdir /s node_modules
   ```
3. Reinstall:
   ```bash
   npm install
   ```

### Problem: "Cannot find module"

**Solution:**
```bash
npm install
```

### Problem: "Database already exists" when running init-db

**Solution:**
This is normal! The script detects existing database and skips creation.
It will still create/update tables.

---

## 🔄 Resetting the Database

To start fresh:

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Drop and recreate
DROP DATABASE cirp_db;
\q

# Run init script again
npm run init-db
```

---

## 📊 Monitoring

### Check if server is running:
```bash
curl http://localhost:3000/health
```

### View logs:
Server prints all requests to console

### Database queries:
```bash
psql -U postgres -d cirp_db

# View reports
SELECT * FROM reports;

# View users
SELECT email, role FROM users;
```

---

## 🚀 Next Steps

1. ✅ Backend is running
2. ✅ Database is initialized
3. ✅ API endpoints are ready

**Now you can:**
- Test API with Postman
- Connect mobile app
- Connect admin page (Next.js frontend)
- Create reports
- Manage users

---

## 📞 Support

If you encounter issues:

1. Check the console logs
2. Verify PostgreSQL is running
3. Check `.env` configuration
4. Ensure port 3000 is available
5. Try resetting the database

---

## 🎯 Features

✅ **Complete REST API**
✅ **PostgreSQL Database**
✅ **JWT Authentication**
✅ **Role-Based Access Control**
✅ **File Upload Support**
✅ **Activity Logging**
✅ **Statistics & Analytics**
✅ **Comments System**
✅ **Notification System**
✅ **Audit Trail**

---

## 📝 Notes

- Server auto-restarts on code changes in dev mode (`npm run dev`)
- All passwords are hashed with bcrypt
- JWT tokens expire after 7 days
- Database uses UUIDs for primary keys
- All timestamps are in UTC
- CORS is configured for localhost and GitHub Pages

---

**🎉 You're all set! Happy coding!**
