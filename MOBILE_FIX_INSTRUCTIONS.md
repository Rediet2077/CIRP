# 📱 MOBILE APP NETWORK FIX

## Problem:
Mobile app shows: **"Network error: TimeoutException after 0:00:30"**

This happens because Windows Firewall is blocking incoming connections to the backend on port 3000.

---

## Solution: Add Firewall Rule

### Option 1: Run Batch File (EASIEST)

1. **Right-click** on `FIX_MOBILE_NETWORK.bat`
2. Select **"Run as administrator"**
3. Click **Yes** on the prompt
4. Wait for "Done!" message
5. **Close and reopen** the CIRP app on your phone
6. Try logging in again

---

### Option 2: Manual PowerShell Command

1. **Right-click** on PowerShell
2. Select **"Run as administrator"**
3. Run this command:
```powershell
New-NetFirewallRule -DisplayName "CIRP Backend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

---

### Option 3: Windows Firewall GUI

1. Press **Windows Key**
2. Type: **Windows Defender Firewall**
3. Click **Advanced settings**
4. Click **Inbound Rules** → **New Rule**
5. Select **Port** → Next
6. **TCP** and **Specific local ports**: `3000` → Next
7. **Allow the connection** → Next
8. Check all (Domain, Private, Public) → Next
9. Name: `CIRP Backend` → Finish

---

### Option 4: Temporary - Disable Firewall (NOT RECOMMENDED)

**For testing only!**
1. Press **Windows Key**
2. Type: **Windows Defender Firewall**
3. Click **Turn Windows Defender Firewall on or off**
4. Turn off for **Private network**
5. Click **OK**
6. **Try mobile app**
7. **TURN IT BACK ON after testing!**

---

## After Fixing:

### Test if it worked:

1. **Open phone browser**
2. Go to: `http://192.168.8.60:3000/health`
3. Should see: `{"status":"ok",...}`

If you see this, the firewall is fixed!

### Then try mobile app:

1. **Open CIRP app**
2. **Login**:
   - Email: `redietsharew231@gmail.com`
   - Password: [your password]
3. Should work now! ✅

---

## 🔑 Password Reset (if you forgot):

If you don't remember your password, I can reset it in the database.

Common passwords you might have used:
- `Test123!`
- `Password123`
- `Rediet123`
- `Admin@123`

Let me know if none work and I'll reset it!

---

## ✅ What This Fixes:

**Before**: Mobile → Network → ❌ Windows Firewall blocks → Backend  
**After**: Mobile → Network → ✅ Firewall allows → Backend

The firewall rule tells Windows: "Allow incoming connections to port 3000 from the network"

---

**Run `FIX_MOBILE_NETWORK.bat` as administrator and try again!** 🚀
