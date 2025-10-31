# Quick Start Guide - NSSM Integration

## ✅ What's Been Updated

All files have been updated to use **NSSM** instead of Windows Service framework:

1. ✅ `WindowSupportGuardian.py` - Simplified (no service code)
2. ✅ `WindowSupportGuardian.spec` - Updated (no pythonservice)  
3. ✅ `rebuild_all.ps1` - Updated (copies NSSM)
4. ✅ `INSTALL_WindowSupport.bat` - Updated (uses NSSM commands)

---

## 🚀 Next Steps

### Step 1: Verify NSSM is Present
```cmd
dir nssm.exe
```
**Expected:** `nssm.exe` should be in your project root (~500KB)

If missing, download from: https://nssm.cc/download  
Extract: `nssm-2.24\win64\nssm.exe` → project root

---

### Step 2: Rebuild All Executables
```powershell
PowerShell -ExecutionPolicy Bypass -File .\rebuild_all.ps1
```

**What this does:**
- Cleans old builds
- Builds all 3 executables with new simplified Guardian
- Copies everything to `dist\WindowSupport\`
- **Includes `nssm.exe` in distribution**

**Verify after build:**
```cmd
dir dist\WindowSupport\nssm.exe
dir dist\WindowSupport\WindowSupportGuardian\WindowSupportGuardian.exe
```

---

### Step 3: Test Installation
```cmd
cd dist\WindowSupport
```

**Right-click:** `INSTALL_WindowSupport.bat`  
**Select:** "Run as Administrator"

**Follow prompts:**
1. Select target user
2. Wait for file copying
3. Confirm Defender exclusions
4. Run Staff ID selector
5. Wait for WindowPowerShellProvider installation
6. **Watch Guardian service install with NSSM** ← New!

---

### Step 4: Verify Service
```cmd
# Check service is running
sc query WindowSupportGuardian

# Should show:
# STATE: RUNNING
# START_TYPE: AUTO_START
```

```cmd
# Check service configuration
sc qc WindowSupportGuardian

# BINARY_PATH_NAME should point to:
# C:\Users\[USER]\AppData\Local\WindowSupport\WindowSupportGuardian\WindowSupportGuardian.exe
# (NOT pythonservice.exe!)
```

---

### Step 5: Check Logs
```cmd
# View Guardian log
type C:\Users\[USER]\AppData\Local\WindowSupport\logs\WindowSupportGuardian.log

# Should show:
# [timestamp] Guardian started - Monitoring WindowPowerShellProvider
# [timestamp] Log file: C:\Users\...\WindowSupport\logs\WindowSupportGuardian.log
# [timestamp] Process not running for user [USER], attempting restart...
# [timestamp] Process started successfully
```

---

## 🎯 What's Different Now

### Old Installation (Broken)
```
WindowSupportGuardian.exe install
  ↓
Looking for pythonservice.exe... NOT FOUND!
  ↓
Service registration fails or shows "Manual"
  ↓
Can't start, wrong path, errors
```

### New Installation (Works!)
```
nssm.exe install WindowSupportGuardian [path to exe]
  ↓
NSSM wraps the exe as a proper Windows Service
  ↓
Service installs correctly with "Automatic" startup
  ↓
Service starts immediately and monitors properly
  ↓
Logs to file for easy debugging
```

---

## 🔍 Troubleshooting

### Problem: "NSSM not found" during installation
**Solution:**
```cmd
# Make sure nssm.exe is in dist\WindowSupport\
copy nssm.exe dist\WindowSupport\
```

### Problem: Service shows "Manual" startup
**This should NOT happen anymore with NSSM!**

If it does:
```cmd
cd C:\Users\[USER]\AppData\Local\WindowSupport
nssm.exe set WindowSupportGuardian Start SERVICE_AUTO_START
nssm.exe restart WindowSupportGuardian
```

### Problem: Service won't start
**Check logs:**
```cmd
type C:\Users\[USER]\AppData\Local\WindowSupport\logs\guardian_stderr.log
```

**Verify exe exists:**
```cmd
dir C:\Users\[USER]\AppData\Local\WindowSupport\WindowSupportGuardian\WindowSupportGuardian.exe
```

### Problem: Guardian not monitoring
**Check Guardian is running:**
```cmd
tasklist | findstr WindowSupportGuardian
```

**Check log file:**
```cmd
type C:\Users\[USER]\AppData\Local\WindowSupport\logs\WindowSupportGuardian.log
```

---

## 📋 Manual Testing (Optional)

You can now test Guardian **without installing as a service:**

```cmd
cd C:\Users\[USER]\AppData\Local\WindowSupport\WindowSupportGuardian
WindowSupportGuardian.exe
```

**You'll see:**
```
Starting WindowSupport Guardian...
This will monitor and restart WindowPowerShellProvider if needed.
Press Ctrl+C to stop (when testing manually)

[2025-10-29 14:30:00] Guardian started - Monitoring WindowPowerShellProvider
[2025-10-29 14:30:00] Log file: C:\Users\...\WindowSupport\logs\WindowSupportGuardian.log
...
```

**Press Ctrl+C to stop testing**

---

## ✅ Success Indicators

After installation, you should see:

1. **Services.msc:**
   - Service Name: `WindowSupportGuardian`
   - Display Name: `Window Support Guardian Service`
   - Status: `Running`
   - Startup Type: `Automatic`
   - Path to executable: Points to Guardian.exe (NOT pythonservice.exe)

2. **Task Manager:**
   - `WindowSupportGuardian.exe` running under SYSTEM account
   - `WindowPowerShellProvider.exe` running under user account

3. **Registry:**
   - `HKLM\SOFTWARE\WindowSupport\GuardianExePath` = correct path
   - `HKLM\SOFTWARE\WindowSupport\ProviderExePath` = correct path

4. **Logs:**
   - `WindowSupportGuardian.log` being updated every 30 seconds
   - No errors in guardian_stderr.log

---

## 🎉 All Done!

Your WindowSupport is now using NSSM for rock-solid service management:
- ✅ No pythonservice.exe issues
- ✅ Reliable auto-start
- ✅ Automatic crash recovery
- ✅ Easy debugging with log files
- ✅ Simpler, maintainable code

**Ready to deploy to other machines:**
- Just copy `dist\WindowSupport\` folder
- Run `INSTALL_WindowSupport.bat` as Administrator
- Everything works!

---

*For detailed technical information, see: NSSM_INTEGRATION_SUMMARY.md*

