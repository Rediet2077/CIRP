# Test Admin Page - Photo Display Fix

## 🚀 Services Running
- ✅ Backend API: http://localhost:3002 (RESTARTED with fixes)
- ✅ Admin Page: http://localhost:3000 (Hot-reloaded with fixes)
- ✅ Mobile App: Connected to backend
- ✅ AI Service: Running on port 8001

## 🔧 Fixes Applied
1. **Photo Display**: Backend now adds `data:image/jpeg;base64,` prefix to images
2. **Link Asset**: Added missing `asset_id` column to database
3. **Schema Validation**: Fixed `contractor_company` nullable issue
4. **UI Component**: Added photo grid display in report details

## 📋 Test Instructions

### Test 1: View Report with Photos (MAIN TEST)
1. **Open browser**: `http://localhost:3000`
2. **Login**: 
   - Email: `roads.admin@city.gov`
   - Password: `Roads@2024`
3. **Navigate**: Click "Reports" in the sidebar
4. **Open Report**: Click on any report (e.g., REP-8694A627 - "Road Damage: Pothole")
5. **✅ VERIFY**: You should see:
   - "Citizen Uploaded Photos" section
   - Photos in a 2-column grid
   - Images load properly (not broken)
   - Click photo to view full size

### Test 2: Link Asset to Report
1. **Open Report**: Click on REP-D0FDEC35 (report without linked asset)
2. **Find Section**: "Suggested Nearby GIS Assets"
3. **Click Button**: "Link Asset" on any suggested asset
4. **✅ VERIFY**: Asset links successfully, no error message

### Test 3: Accept Report & Create Task
1. **Find New Report**: Look for reports with status "NEW" or "PENDING"
2. **Click Button**: "Accept Report & Dispatch Task"
3. **Fill Form**:
   - **Assigned Priority SLA**: Select "MEDIUM"
   - **Assign Field Technician**: Select "staff-rd-01"
   - **Expected Completion Deadline**: Pick a future date (e.g., 08/20/2026)
   - **Field Work Order Instructions**: Type "Inspect and repair pothole"
   - **Internal Operations Note**: Type "Parts requested from depot"
4. **Click**: "Confirm Intake & Dispatch Task"
5. **✅ VERIFY**: 
   - No errors (no "2 issues" badge)
   - Success message appears
   - Report status changes to "ACCEPTED"

### Test 4: View My Reports (Mobile User)
1. **Logout** from admin account
2. **Login** with mobile user:
   - Email: `redietsharew231@gmail.com`
   - Password: `rediet123`
3. **Navigate**: Go to "My Reports" (if there's a citizen view)
4. **✅ VERIFY**: User's 5 reports appear with photos

## 🐛 Debug: If Photos Don't Show

### Check Browser Console
1. **Open DevTools**: Press F12
2. **Go to Console tab**
3. **Look for errors**: Any errors related to images?
4. **Check Network tab**: 
   - Go to Network tab
   - Reload the report page
   - Find the API request to `/api/reports/{id}`
   - Click on it
   - Go to "Response" tab
   - Look for `media_photos` array
   - **✅ Should start with**: `"data:image/jpeg;base64,/9j/..."`

### Check Backend Response
In PowerShell:
```powershell
# Check if backend is adding the prefix
Invoke-RestMethod -Uri "http://localhost:3002/health"
# Should return: {"status":"ok",...}
```

### Force Refresh Browser
1. **Hard Refresh**: Press Ctrl + Shift + R
2. **Clear Cache**: Ctrl + Shift + Delete → Clear cache
3. **Reload Page**

## 📸 Expected Report Details View

```
┌─────────────────────────────────────────────────┐
│ REP-8694A627          REJECTED      MEDIUM      │
│ Category: Road Damage • Submitted: 2026-10-27   │
├─────────────────────────────────────────────────┤
│ Road Damage: Pothole                            │
│ Hello                                           │
│                                                 │
│ Citizen Uploaded Photos                         │
│ ┌─────────────┐ ┌─────────────┐               │
│ │   Photo 1   │ │   Photo 2   │               │
│ │  [Image]    │ │  [Image]    │               │
│ └─────────────┘ └─────────────┘               │
│                                                 │
│ AI Category Prediction                          │
│ Road Damage (94% Confidence)                    │
│                                                 │
│ Duplicate Detection                             │
│ No duplicate indicator returned                 │
└─────────────────────────────────────────────────┘
```

## 🎯 Success Criteria
- ✅ Photos display in report details (not broken image icon)
- ✅ Link Asset button works without database errors
- ✅ Accept Report form submits successfully
- ✅ No schema validation errors in console
- ✅ Can click photo to view full size

## 📊 Database Verification

If you want to verify the database directly:
```bash
sqlite3 "C:\Users\Usuario\Documents\CIRP\backend\database\cirp.db"
```

Then run:
```sql
-- Check reports have asset_id column
PRAGMA table_info(reports);

-- Check images exist
SELECT 
  r.report_code,
  COUNT(ri.id) as image_count,
  LENGTH(ri.image_url) as image_size
FROM reports r
LEFT JOIN report_images ri ON r.id = ri.report_id
WHERE r.user_id = 'eae9882a-6323-4f7a-81e9-fc1cab2d1bf9'
GROUP BY r.id;
```

Expected result: 4-5 reports with image_count=1 and image_size ~100KB-120KB

## 🔄 If Still Not Working

### Restart Everything
1. Stop all services
2. Run from CIRP root:
```bash
# Stop processes
Ctrl+C on each terminal

# Restart backend
cd backend
node server.js

# Restart admin (in new terminal)
cd "admin page"
npm run dev

# Wait 10 seconds, then test again
```

### Check Backend Logs
```powershell
# In backend terminal, you should see:
GET /api/reports/{id} 200 in XXms
```

### Check Admin Logs
```powershell
# In admin terminal, you should see:
✓ Compiled successfully
GET /dashboard/reports 200 in XXms
```

## 📝 Notes
- Photos are stored as base64 JPEG (100KB-120KB each)
- Backend automatically adds data URI prefix now
- Admin UI shows photos in aspect-video grid
- Click any photo to open in new tab at full resolution

---
**Status**: All fixes applied and services restarted
**Next**: Test in browser at http://localhost:3000
