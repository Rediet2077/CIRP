# Fix Network Error - Allow Windows Firewall

## Problem
Your phone shows "Network error" when trying to login because **Windows Firewall is blocking port 3000**.

## Solution: Allow Port 3000 Through Firewall

### Option 1: PowerShell (Run as Administrator)

1. **Right-click** on PowerShell
2. Select **"Run as Administrator"**
3. Run this command:

```powershell
New-NetFirewallRule -DisplayName "CIRP Backend Server" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow -Profile Any
```

### Option 2: Windows Defender Firewall GUI

1. Press **Windows key** and search for **"Windows Defender Firewall"**
2. Click **"Advanced settings"** (on the left)
3. Click **"Inbound Rules"** (on the left)
4. Click **"New Rule..."** (on the right)
5. Select **"Port"** → Next
6. Select **"TCP"** → Enter **"3000"** in "Specific local ports" → Next
7. Select **"Allow the connection"** → Next
8. Check all: **Domain**, **Private**, **Public** → Next
9. Name it: **"CIRP Backend Server"** → Finish

### Option 3: Temporarily Disable Firewall (Not Recommended)

**Only for testing - NOT recommended for regular use:**

1. Search for **"Windows Defender Firewall"**
2. Click **"Turn Windows Defender Firewall on or off"**
3. Select **"Turn off"** for Private and Public networks
4. Try logging in on your phone
5. **Remember to turn it back on!**

---

## After Fixing Firewall

1. **Open the CIRP app on your phone**
2. **Login with:**
   - Email: `citizen@test.com`
   - Password: `Test@123`
3. **It should work now!**

---

## Quick Test

After adding the firewall rule, test if the server is accessible:

```powershell
Test-NetConnection -ComputerName 192.168.0.160 -Port 3000
```

You should see: **"TcpTestSucceeded : True"**

---

## If Still Not Working

1. **Check both devices are on same WiFi:**
   - On phone: Settings → WiFi → Check network name
   - On PC: Check WiFi icon in taskbar

2. **Check backend is running:**
   ```powershell
   curl http://localhost:3000/health
   ```
   Should return: `{"status":"ok",...}`

3. **Try from another device on same network:**
   ```powershell
   curl http://192.168.0.160:3000/health
   ```

---

## Current Status

✅ Backend server: Running on http://192.168.0.160:3000  
✅ Database: Initialized with test users  
✅ Mobile app: Configured to use 192.168.0.160  
❌ Firewall: Blocking port 3000 (needs fix above)
