# CIRP Mobile App - Login Credentials

## 📱 Test Account

Use these credentials to login to the mobile app:

```
Email:     test@cirp.com
Password:  test123
```

## 👤 User Details

- **Name:** Rediet Shewit
- **Phone:** +1234567890
- **Role:** CITIZEN
- **Status:** Active & Verified

## 🔌 Backend Connection

- **Backend URL:** http://192.168.137.167:8000
- **AI Service URL:** http://192.168.137.167:8001

## ✅ What to Test

1. **Login Flow:**
   - Open the app on your phone
   - Skip/complete onboarding
   - Enter email: `test@cirp.com`
   - Enter password: `test123`
   - Click Login

2. **Home Dashboard:**
   - View welcome message with your name
   - Browse issue categories (Streetlight, No Water, Damage, etc.)
   - See recent issues list

3. **Report Issue:**
   - Click FAB (Floating Action Button) or category card
   - Select category
   - Fill in issue details
   - Add photos
   - Set location
   - Submit report

4. **My Reports:**
   - Navigate to Reports tab
   - View all/in-progress/resolved reports
   - Pull to refresh

5. **Profile:**
   - Navigate to Profile tab
   - View stats (23 Reports, 18 Resolved, 5 Pending)
   - Access settings
   - Logout

## 🎨 App Features

- ✅ Splash screen with CIRP logo
- ✅ 3-page onboarding experience
- ✅ Login & Registration
- ✅ Home dashboard with categories
- ✅ Report issue form with photo upload
- ✅ My reports with status filters
- ✅ Profile with stats and settings
- ✅ Bottom navigation
- ✅ API integration ready

## 🚀 Next Steps

To create additional test users, run:

```powershell
cd c:\Users\Usuario\Documents\CIRP\backend
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.create_user(email='YOUR_EMAIL', phone_number='YOUR_PHONE', password='YOUR_PASSWORD', first_name='FIRST_NAME', last_name='LAST_NAME'); print(f'User {user.email} created!')"
```

## 📝 Notes

- The app is running in **debug mode** with **hot reload** enabled
- Changes to the code will automatically update on your phone
- Backend API must be running on port 8000
- AI service must be running on port 8001
- Phone and computer must be on the same WiFi network (192.168.137.x)
