# 🧪 Test Complete CIRP System - Step by Step Guide

## ✅ System Status

**Backend**: ✅ Running on http://192.168.8.60:3000
**Admin Page**: ✅ Running on http://localhost:3001  
**Mobile App**: ✅ Running on phone SM A107F
**Database**: ✅ SQLite with all tables configured

---

## 📱 STEP 1: Test on Mobile App

### A. Login (You already did this!)
- ✅ Registered user: Rediet (redietsharew231@gmail.com)
- ✅ Verified with OTP
- ✅ Login successful
- ✅ Name "Rediet" appears on dashboard

### B. Submit a Report

**On your phone:**

1. **Open the CIRP app** (if not already open)

2. **From Home screen** → Click the **"Report Problem"** button (big green/purple button)

3. **Pick Location**:
   - Allow GPS permission if prompted
   - The map should show your current location
   - Or tap "Change Location" to pick a different spot
   - Click "Next"

4. **Add Details**:
   - **Category**: Select **"Streetlight"** ⚡ (to test Electrical Services routing)
   - **Subcategory**: "Not working"
   - **Severity**: Select "High"
   - **When**: "Today"
   - **Description**: "Streetlight not working on main road"
   - Click "Next"

5. **Add Photo** (optional):
   - Take photo or skip
   - Click "Next"

6. **Review & Submit**:
   - Check the summary
   - Click **"Submit Report"**

7. **Expected Result**:
   - ✅ Success message: "Report submitted successfully"
   - ✅ You're returned to home screen

---

## 🔍 STEP 2: Verify in Database

After submitting, I'll check if the report is stored with the correct department routing.

**What should happen:**
- Report stored with `user_id` = Rediet's ID
- `category_id` = Streetlight
- `department_id` = Electrical Services (auto-assigned!)
- GPS coordinates captured
- Status = "pending"

---

## 🖥️ STEP 3: Test Admin Page

### A. Login as Electrical Services Admin

1. **Open browser**: http://localhost:3001

2. **Login with**:
   - Email: `electrical.services@cirp.com`
   - Password: `Admin@123`

3. **Expected Result**:
   - ✅ Login successful
   - ✅ Dashboard shows "Electrical Services" department
   - ✅ **Only shows Streetlight reports** (your submitted report should appear!)
   - ✅ Report details: title, status, location, submitted by "Rediet"

### B. Test Department Filtering

4. **Submit another report** from mobile with different category:
   - Category: **"Water Leakage"** 💧
   - Description: "Water pipe burst"

5. **Check admin page**:
   - ✅ Electrical Services admin should **NOT see** the water report
   - ✅ Water report has `department_id` = Water & Sewage

6. **Logout and login as Water admin**:
   - Email: `water.&.sewage@cirp.com`
   - Password: `Admin@123`
   - ✅ Should see the water report
   - ✅ Should NOT see the streetlight report

### C. Login as System Admin (See ALL Reports)

7. **Logout and login as system admin**:
   - Email: `admin@cirp.com`
   - Password: `Test@123`

8. **Expected Result**:
   - ✅ Sees **BOTH** reports (streetlight AND water)
   - ✅ Can see all departments' reports
   - ✅ Can filter by department, status, category

---

## 📊 STEP 4: Verify Mobile Dashboard Updates

### A. My Reports

1. **On mobile app** → Go to **"Reports"** tab (bottom navigation)

2. **Expected Result**:
   - ✅ Shows list of your submitted reports
   - ✅ Each report shows: title, category, status, date
   - ✅ Can tap to see details

### B. Recent Reports on Home

3. **Go to Home tab**

4. **Scroll down to "Recent Issues" section**

5. **Expected Result**:
   - ✅ Shows your recently submitted reports
   - ✅ Real data from database (not mock data)
   - ✅ Status badges (pending, assigned, etc.)

---

## 🎯 What to Verify

### ✅ Registration & Login
- [x] User registered with OTP verification
- [x] User can login
- [x] Name displays on dashboard
- [x] User stored in database with `is_email_verified=1`

### 📝 Report Submission
- [ ] Report can be submitted from mobile
- [ ] GPS coordinates captured
- [ ] Photo uploaded (optional)
- [ ] Report stored in database
- [ ] **department_id auto-assigned** based on category

### 🏛️ Department Routing
- [ ] Streetlight report → Electrical Services (`department_id` matches)
- [ ] Water report → Water & Sewage
- [ ] Road report → Public Works
- [ ] Garbage report → Sanitation

### 🖥️ Admin Page
- [ ] Electrical Services admin sees ONLY Streetlight reports
- [ ] Water admin sees ONLY Water reports
- [ ] System admin sees ALL reports
- [ ] Reports display with correct user name ("Rediet")
- [ ] Can update report status

### 📱 Mobile Dashboard
- [ ] "My Reports" tab shows submitted reports
- [ ] "Recent Issues" on home shows real reports
- [ ] Status updates reflect database changes
- [ ] Can view report details

---

## 🔑 Admin Credentials Reference

| Department | Email | Password |
|-----------|-------|----------|
| **System Admin** (ALL) | admin@cirp.com | Test@123 |
| **Electrical Services** ⚡ | electrical.services@cirp.com | Admin@123 |
| **Water & Sewage** 💧 | water.&.sewage@cirp.com | Admin@123 |
| **Public Works** 🛣️ | public.works@cirp.com | Admin@123 |
| **Sanitation** 🗑️ | sanitation@cirp.com | Admin@123 |

---

## 📋 Test Scenarios

### Scenario 1: Streetlight Report
1. Submit "Streetlight not working" from mobile
2. Check database: `department_id` = Electrical Services
3. Login as electrical.services@cirp.com
4. Verify: Report appears in dashboard
5. Update status to "Assigned"
6. Check mobile: Status updated

### Scenario 2: Water Report
1. Submit "Water pipe burst" from mobile
2. Check database: `department_id` = Water & Sewage
3. Login as water.&.sewage@cirp.com
4. Verify: Report appears
5. electrical.services@cirp.com should NOT see this report

### Scenario 3: Cross-Department Verification
1. Submit 4 reports (one from each category)
2. Each department admin should see ONLY their reports
3. System admin should see ALL 4 reports
4. Mobile "My Reports" should show all 4

---

## 🐛 Troubleshooting

### Mobile App Issues

**"Network Error"**
- Check backend is running: http://192.168.8.60:3000/health
- Verify phone and PC on same WiFi
- Check Windows Firewall allows port 3000

**"Invalid Token"**
- Logout and login again
- Clear app data and login

**Report Not Submitting**
- Check GPS permission granted
- Verify category selected
- Check description not empty

### Admin Page Issues

**Login Failed**
- Verify email is exact (including dots and special chars)
- Password is case-sensitive: `Admin@123`
- For system admin: `Test@123`

**Reports Not Showing**
- Verify reports exist in database
- Check department_id matches user's department
- System admin should see all regardless

---

## 📞 Next Steps After Testing

Once you've verified everything works:

1. **Report any issues you find**
2. **Confirm which features work perfectly**
3. **Tell me what needs adjustment**

I'm ready to:
- Fix any bugs you discover
- Adjust the UI/UX
- Add more features
- Optimize performance
- Deploy to production

---

## 🎉 Expected Final Result

**A complete working system where:**

✅ Citizens register → verify email → login  
✅ Citizens submit reports with GPS and photos  
✅ Reports auto-route to correct department  
✅ Department admins see only their reports  
✅ System admin sees everything  
✅ Status updates flow back to mobile app  
✅ Real-time data everywhere (no mock data!)  

**Ready to test! 🚀**
