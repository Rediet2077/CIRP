# 📱 CIRP Mobile App - Testing Guide

## ✅ Backend Integration Status

### Report Submission Flow:
1. **User submits report** → Mobile app sends to `/api/reports` (POST)
2. **Backend receives report** → Validates category_id
3. **Auto-department assignment** → Looks up `category.department_id`
4. **Report created** → Stored with correct `department_id`
5. **Department admin sees it** → Report appears in their dashboard

### Category → Department Mapping (Verified):
```
Road Damage    → Public Works
Water Leakage  → Water & Sewage
Garbage        → Sanitation
Streetlight    → Electrical Services
Drainage       → Water & Sewage
Other          → Public Works
```

✅ **Integration is correct!** Reports will automatically route to the right department.

---

## 🚀 Running the Mobile App

### Option 1: Quick Launch (Recommended)
```bash
# Double-click this file:
RUN_MOBILE_APP.bat
```

This will:
1. Check Flutter installation
2. Get dependencies
3. Launch Pixel 7a emulator
4. Run the app

### Option 2: Manual Launch

#### Step 1: Start Android Emulator
```bash
flutter emulators --launch Pixel_7a
# Wait 30-60 seconds for emulator to fully boot
```

#### Step 2: Run the App
```bash
cd mobile
flutter pub get
flutter run
```

### Option 3: Physical Device

**If using your connected phone (R9AN9139KVJ):**

1. On your phone: Enable USB debugging
2. Check for authorization dialog on phone
3. Update API configuration:

```dart
// In mobile/lib/core/constants/api_constants.dart
static const String baseUrl = _physicalDeviceBaseUrl; // Line 13
```

4. Find your PC's IP address:
```bash
ipconfig
# Look for "IPv4 Address" under your active network adapter
```

5. Update the IP in `api_constants.dart`:
```dart
static const String _physicalDeviceBaseUrl = 'http://YOUR_PC_IP:3002';
```

6. Run: `flutter run -d R9AN9139KVJ`

---

## 🧪 Testing the Integration

### Test Case 1: Submit a Report
1. **Login** to mobile app as `citizen@test.com` / `Test@123`
2. **Create new report**:
   - Title: "Broken streetlight"
   - Category: Streetlight
   - Description: "Light not working"
   - Location: Use map or enter address
3. **Submit**
4. **Verify in Admin Dashboard**:
   - Login as `electrical.services@cirp.com` / `Test@123`
   - Check reports list
   - ✅ Should see the new report with status "NEW"

### Test Case 2: Multiple Categories
Try each category and verify it goes to correct department:
- Road Damage → `public.works@cirp.com`
- Water Leakage → `water.sewage@cirp.com`
- Garbage → `sanitation@cirp.com`
- Streetlight → `electrical.services@cirp.com`

### Test Case 3: Check Report Details
1. Submit report from mobile
2. Note the report ID/code
3. Login to admin dashboard
4. Find the report
5. ✅ Verify all fields match:
   - Title, description, location
   - Category name
   - Department assignment
   - Reporter info (if not anonymous)

---

## 🔧 Mobile App Configuration

### Current Settings:
```
Backend API: http://10.0.2.2:3002/api
Device: Android Emulator
Port: 3002 (Backend)
Auth: JWT Token
```

### API Endpoints Mobile Uses:
- POST `/api/auth/login` - User login
- POST `/api/auth/register` - New user registration
- GET `/api/categories` - List all categories
- POST `/api/reports` - Submit new report
- GET `/api/reports` - Get user's reports
- GET `/api/reports/:id` - Get report details
- POST `/api/reports/:id/comments` - Add comment
- GET `/api/notifications` - Get notifications

---

## 📊 Expected Flow

### Mobile App (Citizen):
1. Citizen opens app
2. Sees issue in their area
3. Takes photo
4. Selects category (e.g., "Water Leakage")
5. Adds description and location
6. Submits report

### Backend (Auto-Processing):
1. Receives POST to `/api/reports`
2. Validates user is authenticated
3. Looks up category: "Water Leakage"
4. Finds department_id from category
5. Creates report with `department_id = water_sewage_dept_id`
6. Returns success

### Admin Dashboard (Department Admin):
1. `water.sewage@cirp.com` logs in
2. Dashboard shows "7 reports" (or 8 after new one)
3. Filters by department automatically
4. Sees new "Water Leakage" report
5. Can assign, update status, add comments

---

## 🐛 Troubleshooting

### Emulator won't start:
```bash
# Check if already running:
adb devices

# Kill and restart:
adb kill-server
adb start-server
flutter emulators --launch Pixel_7a
```

### App can't connect to backend:
```bash
# Verify backend is running:
curl http://localhost:3002/health

# Check emulator can reach host:
adb shell ping 10.0.2.2
```

### "Device not authorized":
- Check your phone for USB debugging dialog
- Select "Always allow from this computer"
- Re-run `flutter devices`

### Flutter issues:
```bash
flutter doctor
flutter clean
flutter pub get
flutter run
```

---

## 📱 Mobile App Features

### Implemented:
- ✅ User authentication (login/register)
- ✅ Report submission with photos
- ✅ Category selection
- ✅ Location picker (map)
- ✅ Report history
- ✅ Report status tracking
- ✅ Comments on reports
- ✅ Notifications
- ✅ Multi-language support

### Backend Features:
- ✅ JWT authentication
- ✅ Auto-department routing
- ✅ Image upload support
- ✅ Report status management
- ✅ Comment system
- ✅ Activity logging

---

## 🎯 Test Credentials

### For Mobile App Testing:

**Citizen Accounts:**
```
Email: citizen@test.com
Password: Test@123

Email: redietsharew231@gmail.com
Password: Test@123
```

**Admin Accounts** (for dashboard verification):
```
System Admin: admin@cirp.com / Test@123
Public Works: public.works@cirp.com / Test@123
Water & Sewage: water.sewage@cirp.com / Test@123
Sanitation: sanitation@cirp.com / Test@123
Electrical: electrical.services@cirp.com / Test@123
```

---

## ✅ Integration Checklist

- [x] Backend running on port 3002
- [x] Mobile API config updated to 3002
- [x] Categories mapped to departments
- [x] Report submission endpoint working
- [x] Auto-department assignment logic verified
- [x] Admin dashboard shows reports by department
- [x] User authentication working
- [ ] Mobile app running (run RUN_MOBILE_APP.bat)
- [ ] Test report submission
- [ ] Verify in admin dashboard

---

## 🚀 Quick Start Commands

```bash
# 1. Start backend (if not running)
cd backend
npm start

# 2. Start mobile app
cd mobile
flutter pub get
flutter emulators --launch Pixel_7a
# Wait 30 seconds
flutter run
```

---

**Ready to test!** The integration is verified and ready. Just run the mobile app! 🎉
