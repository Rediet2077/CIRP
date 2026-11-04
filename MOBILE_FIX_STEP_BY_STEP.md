# 📱 FIX MOBILE APP - STEP BY STEP

## Current Problem:
Your phone shows: **"Network error: TimeoutException"**

This means your phone can't reach the backend because Windows Firewall is blocking it.

---

## SOLUTION - Follow These Steps EXACTLY:

### Step 1: Find the Batch File
1. Open File Explorer
2. Go to: `C:\Users\Usuario\Documents\CIRP`
3. Find the file: `FIX_MOBILE_NETWORK.bat`

### Step 2: Run as Administrator
1. **RIGHT-CLICK** on `FIX_MOBILE_NETWORK.bat`
2. Select **"Run as administrator"** (NOT just "Open")
3. Windows will ask: "Do you want to allow this app to make changes?"
4. Click **YES**

### Step 3: Wait
- A black window will open
- It will say "Creating firewall rule..."
- Wait for it to say "Done!"
- Press any key to close

### Step 4: Test
1. On your **phone's browser** (Chrome/Samsung Internet)
2. Go to: `http://192.168.8.60:3000/health`
3. You should see: `{"status":"ok",...}`

### Step 5: Try Mobile App Again
1. **Close** the CIRP app completely (swipe away from recent apps)
2. **Reopen** the CIRP app
3. **Try login** again

---

## If You Can't Find the Batch File:

Run this command manually:

1. Press **Windows Key**
2. Type: `PowerShell`
3. **Right-click** on "Windows PowerShell"
4. Select **"Run as administrator"**
5. Copy and paste this command:

```powershell
netsh advfirewall firewall add rule name="CIRP Backend - Port 3000" dir=in action=allow protocol=TCP localport=3000
```

6. Press **Enter**
7. Should say "Ok."

---

## Alternative: Temporarily Disable Firewall (for testing)

**ONLY FOR TESTING - Turn it back on after!**

1. Press **Windows Key**
2. Type: `Windows Defender Firewall`
3. Click: **Turn Windows Defender Firewall on or off**
4. Under **Private network settings**: Select **Turn off**
5. Click **OK**
6. **Try mobile app now**
7. **IMPORTANT**: Turn firewall back ON after testing!

---

## How to Know If It Worked:

### Test 1 - Phone Browser:
Go to: `http://192.168.8.60:3000/health`
- ✅ See JSON response = Firewall is fixed!
- ❌ Timeout/error = Firewall still blocking

### Test 2 - Mobile App:
Try login again
- ✅ Works = Fixed!
- ❌ Still timeout = Need to check firewall

---

## Your Login Credentials:

**Email**: `redietsharew231@gmail.com`

**Password**: Try these in order:
1. `Test123!`
2. `Password123`
3. `Rediet123`
4. `Admin@123`

If NONE of these work, tell me and I'll reset your password!

---

**The key is: Run the batch file AS ADMINISTRATOR** 🔑
