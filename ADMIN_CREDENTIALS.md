# CIRP Admin Panel - User Credentials & Access Guide

## 🔐 Admin Credentials

### Super Admin (Full System Access)
```
Email:    superadmin@cirp.com
Password: Super@123
Role:     SUPER_ADMIN

Access:
✅ Dashboard
✅ Departments
✅ Users
✅ Reports
✅ Assets
✅ Notifications
✅ Settings
```

### Department Admins (Limited Scope)

#### Road Admin
```
Email:    roadadmin@cirp.com
Password: Road@123
Role:     ROAD_ADMIN
Department: Roads & Transport Department
```

#### Water Admin
```
Email:    wateradmin@cirp.com
Password: Water@123
Role:     WATER_ADMIN
Department: Water & Sanitation Department
```

#### Electricity Admin
```
Email:    electricityadmin@cirp.com
Password: Electricity@123
Role:     ELECTRICITY_ADMIN
Department: Electricity Department
```

#### Drainage Admin
```
Email:    drainageadmin@cirp.com
Password: Drainage@123
Role:     DRAINAGE_ADMIN
Department: Drainage & Flood Management
```

#### Waste Admin
```
Email:    wasteadmin@cirp.com
Password: Waste@123
Role:     WASTE_ADMIN
Department: Sanitation & Waste Management
```

#### Street Light Admin
```
Email:    streetlightadmin@cirp.com
Password: Light@123
Role:     STREETLIGHT_ADMIN
Department: Street Lighting Department
```

#### Public Facilities Admin
```
Email:    facilitiesadmin@cirp.com
Password: Facilities@123
Role:     PUBLIC_FACILITIES_ADMIN
Department: Public Facilities & Buildings
```

### Department Admin Access (All Above)
```
Access:
✅ Dashboard
✅ Reports (Department-specific)
✅ Assets (Department-specific)
✅ Notifications
```

## 🌐 Access URLs

- **Backend API**: http://0.0.0.0:8000
- **Admin Panel (Local)**: http://localhost:3000
- **Admin Panel (Network)**: http://192.168.137.1:3000

## ✅ Testing Instructions

1. **Clear Browser Data**
   - Press `Ctrl + Shift + Delete`
   - Select "All time"
   - Check "Cookies" and "Cached images"
   - Click "Clear data"

2. **Open Browser Console**
   - Press `F12`
   - Go to "Console" tab
   - Watch for debug logs

3. **Login with Super Admin**
   ```
   Email: superadmin@cirp.com
   Password: Super@123
   ```
   - Should see **7 menu items** in sidebar
   - Menu label: "System Administration"

4. **Logout and Login with Department Admin**
   ```
   Email: roadadmin@cirp.com
   Password: Road@123
   ```
   - Should see **4 menu items** in sidebar
   - Menu label: "Department Management"

## 🐛 Debug Logs to Check

Console should show:
```
🔑 Login Success: { email: "...", role: "...", department: "..." }
✅ Role is valid admin role, setting to store
💾 Saving to localStorage
🔐 Auth Session Restore: { hasSession: true, userRole: "...", userEmail: "..." }
✅ Setting role: ...
🔄 Store: Setting currentUserRole to: ...
🔍 AppSidebar Debug: { currentUserRole: "...", navGroupsCount: 1, ... }
```

## 🔧 What Was Fixed

### 1. Zod Schema Issue
- **Problem**: `UserRoleSchema` only accepted `SYSTEM_ADMIN` and `DEPARTMENT_ADMIN`
- **Fix**: Added all 10 role types to the Zod enum

### 2. Role Switcher Removed
- **Problem**: Demo role switcher allowed manual toggle, overriding actual auth
- **Fix**: Removed `UserRoleSwitcher` component from footer

### 3. Session Restoration
- **Problem**: Role was lost on page refresh
- **Fix**: Created `AuthSessionProvider` to restore role from localStorage

### 4. User Display
- **Problem**: Hardcoded demo user names
- **Fix**: Display actual logged-in user info from session

## 📝 Notes

- The role switcher has been **permanently removed**
- Each user now sees menus based on their **actual database role**
- Roles are **preserved across page refreshes**
- Logout properly clears session and cookies
