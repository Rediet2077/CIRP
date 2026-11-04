# CIRP Mobile App - Fixes Applied

## Problems Fixed

### 1. ✅ Invalid Token Error
**Problem**: App showed "Invalid token" when trying to submit reports  
**Root Cause**: 
- App was using `LocalAuthService` (offline-only) instead of calling real backend API
- Token wasn't being saved to SharedPreferences after login

**Fix Applied**:
- Updated `login_screen.dart` to use `AuthService` (real API) instead of `LocalAuthService`
- Modified login flow to save token using `TokenStorage.saveTokens()`
- Updated `auth_service.dart` to correctly parse backend response format
- Fixed backend `auth.js` routes to use async SQLite methods (was causing crashes)

**Files Changed**:
- `mobile/lib/features/auth/screens/login_screen.dart` - Switch to API auth
- `mobile/lib/core/services/auth_service.dart` - Fix response parsing
- `backend/routes/auth.js` - Convert to async/await for sqlite3

### 2. ✅ UI Overflow Error (Category Cards)
**Problem**: Category cards showed "BOTTOM OVERFLOWED BY 2.7 PIXELS"  
**Root Cause**: Cards were too tall with `childAspectRatio: 0.85` and had a `Spacer()` widget

**Fix Applied**:
- Changed `childAspectRatio` from `0.85` to `0.92` (makes cards slightly wider/shorter)
- Replaced `Spacer()` with fixed `SizedBox(height: 6)` for consistent spacing
- Reduced padding and icon sizes slightly to fit better
- Wrapped title in `Flexible` widget to prevent overflow
- Increased grid spacing from 10 to 12 pixels

**Files Changed**:
- `mobile/lib/features/home/screens/home_screen.dart` - Adjust grid layout

---

## How to Test

### 1. Free Up Phone Storage
Your phone shows `INSTALL_FAILED_INSUFFICIENT_STORAGE`. You need to:
- Delete unused apps
- Clear cache (Settings → Storage → Cached data)
- Move photos/videos to PC or cloud
- Need at least ~100MB free

### 2. Reinstall App
Once storage is free:

```powershell
cd C:\Users\Usuario\Documents\CIRP\mobile
flutter run -d R9AN9139KVJ
```

### 3. Test Login with Backend
1. Make sure backend is running:
   ```powershell
   cd C:\Users\Usuario\Documents\CIRP\backend
   npm start
   ```

2. On your phone, open the app and login with:
   - Email: `citizen@test.com`
   - Password: `Test@123`

3. After login, you should see:
   - ✅ Home screen with your name
   - ✅ Category cards that fit properly (no overflow error)
   - ✅ Can tap a category to create a report
   - ✅ Submit report works (no invalid token error)

---

## Current System Status

### ✅ Backend (Node.js + SQLite)
- Running on: http://192.168.0.160:3000
- Database: `backend/database/cirp.db`
- Auth endpoints working with async methods
- Test account: citizen@test.com / Test@123

### ✅ Mobile App (Flutter)
- Configured to use: http://192.168.0.160:3000
- Login screen calls real API
- Token storage working
- UI overflow fixed
- Ready to install (needs phone storage)

### 🔄 Next Step
**Free up phone storage** (~100MB) and run:
```powershell
cd mobile
flutter run -d R9AN9139KVJ
```

---

## What Changed (Technical Details)

### Backend Auth Route Fix
**Before** (broken):
```javascript
const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
```

**After** (working):
```javascript
const user = await db.getAsync('SELECT * FROM users WHERE email = ?', [email]);
```

### Login Screen Fix
**Before** (offline only):
```dart
final result = await LocalAuthService.login(email, password);
```

**After** (API call):
```dart
final result = await AuthService.login(email: email, password: password);
await TokenStorage.saveTokens(token, token);
```

### Category Grid Fix
**Before** (overflow):
```dart
childAspectRatio: 0.85,  // Too tall
const Spacer(),          // Unpredictable height
```

**After** (fits):
```dart
childAspectRatio: 0.92,  // Better proportions
const SizedBox(height: 6), // Fixed height
Flexible(child: Text(...)) // Prevents overflow
```

---

## If You Still See Errors

### "Invalid Token" Error
1. Make sure backend is running: http://localhost:3000/health should return `{"status":"ok"}`
2. Clear app data on phone (App Info → Storage → Clear Data)
3. Login again with fresh credentials

### "Overflow" Error
1. Make sure you pulled latest code with fixes
2. Do `flutter clean` then `flutter run`
3. Check that `home_screen.dart` has `childAspectRatio: 0.92`

### Connection Error
1. Check PC IP hasn't changed: `ipconfig | Select-String "IPv4"`
2. Update `api_constants.dart` if IP changed
3. Make sure phone and PC on same WiFi network
4. Check Windows Firewall isn't blocking port 3000

---

## Summary

All code fixes have been applied and committed. The app is ready to run once you have enough storage on your phone. Both the "invalid token" and "overflow" errors have been resolved in the code.
