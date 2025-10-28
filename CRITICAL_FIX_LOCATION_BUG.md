# Critical Fix: Location Registration Bug

## 🐛 **The Bug**

### **Problem:**
When running the executables from the **build folder** (`dist\WindowSupport\`), they would register themselves in Windows startup using the **wrong path** (the build folder path instead of the installation path).

### **Example:**
```
BAD:  D:\Dawood's work\WindowPowerShell-main\dist\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe
GOOD: C:\Users\avant\AppData\Local\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe
```

### **Impact:**
- Scheduled task points to build folder (won't work after deleting build)
- Application won't start automatically after reboot
- Guardian can't find Provider (wrong location)

---

## ✅ **The Fix**

### **WindowPowerShellProvider.py**

Added location validation in `add_to_startup()`:

```python
# Check if running from correct installation location
expected_location = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'WindowSupport')
current_location = os.path.dirname(exe_path)

if expected_location.lower() not in current_location.lower():
    print("⚠ WARNING: Not running from installed location!")
    print("⚠ Skipping startup registration to avoid registering wrong path.")
    return  # Don't register!
```

**Result:**
- ✅ Only registers startup when running from `C:\Users\...\AppData\Local\WindowSupport\`
- ✅ Shows warning if run from build folder
- ✅ Prevents incorrect path registration

### **WindowSupportGuardian.py**

Added similar warning at startup:

```python
if expected_location.lower() not in current_location.lower():
    print("WARNING: Guardian not running from installed location!")
    print("Please install properly using INSTALL_WindowSupport.bat")
    # Show helpful instructions
```

**Result:**
- ✅ Warns user if run from wrong location
- ✅ Shows correct installation instructions
- ✅ Prevents service registration with wrong path

---

## 🔄 **What You Need to Do**

### **Step 1: Remove Old Incorrect Registration**

If you already ran the exe from the build folder, remove the bad scheduled task:

```batch
schtasks /delete /tn "WindowSupportMonitor" /f
```

### **Step 2: Rebuild with Fixed Code**

```powershell
PowerShell -ExecutionPolicy Bypass -File .\rebuild_all.ps1
```

### **Step 3: Clean Install**

```batch
# Right-click and Run as Administrator
INSTALL_WindowSupport.bat
```

This will:
1. Copy files to correct location (`AppData\Local\WindowSupport`)
2. Create scheduled task with CORRECT path
3. Install Guardian service from CORRECT location

---

## 🎯 **How It Works Now**

### **Scenario 1: Run from Build Folder (Testing)**

```
User runs: D:\...\dist\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe

Application checks location:
  Current:  D:\...\dist\WindowSupport\...
  Expected: C:\Users\...\AppData\Local\WindowSupport\...
  
  ⚠ Mismatch! Skip startup registration.
  ⚠ Show warning message.
```

### **Scenario 2: Run from Installed Location**

```
User runs: C:\Users\avant\AppData\Local\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe

Application checks location:
  Current:  C:\Users\avant\AppData\Local\WindowSupport\...
  Expected: C:\Users\...\AppData\Local\WindowSupport\...
  
  ✓ Match! Register startup with correct path.
  ✓ Create scheduled task.
```

### **Scenario 3: Installer Runs It**

```
INSTALL_WindowSupport.bat:
  1. Copies to: C:\Users\avant\AppData\Local\WindowSupport\
  2. Creates scheduled task with correct path
  3. Runs exe from installed location
  4. Exe detects correct location, confirms registration
```

---

## 📊 **Before vs After**

| Aspect | Before (Buggy) | After (Fixed) |
|--------|----------------|---------------|
| Run from dist | ❌ Registers dist path | ✅ Shows warning, skips registration |
| Run from AppData | ✅ Registers AppData path | ✅ Registers AppData path |
| Scheduled task path | ❌ Could be wrong | ✅ Always correct |
| User experience | ❌ Confusing errors | ✅ Clear warnings |

---

## 🧪 **Testing**

### **Test 1: Run from Build Folder**

```powershell
cd "dist\WindowSupport\WindowPowerShellProvider"
.\WindowPowerShellProvider.exe
```

**Expected:**
```
⚠ WARNING: Not running from installed location!
⚠ Skipping startup registration to avoid registering wrong path.
⚠ This exe should be run from: C:\Users\...\AppData\Local\WindowSupport
⚠ Currently running from: D:\...\dist\WindowSupport\WindowPowerShellProvider
⚠ Please use INSTALL_WindowSupport.bat to install properly.
```

### **Test 2: Run from Installed Location**

```powershell
cd "C:\Users\avant\AppData\Local\WindowSupport\WindowPowerShellProvider"
.\WindowPowerShellProvider.exe
```

**Expected:**
```
Current exe location: C:\Users\avant\AppData\Local\WindowSupport\WindowPowerShellProvider
Expected install location: C:\Users\avant\AppData\Local\WindowSupport
✓ Running from correct installation location
Setting up startup for user: avant
Executable path: C:\Users\avant\AppData\Local\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe
Creating scheduled task...
✓ Scheduled task created successfully!
```

### **Test 3: Verify Scheduled Task Path**

```powershell
schtasks /query /tn "WindowSupportMonitor" /v /fo list | findstr "Task To Run"
```

**Expected:**
```
Task To Run: C:\Users\avant\AppData\Local\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe
```

**NOT:**
```
Task To Run: D:\Dawood's work\...\dist\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe
```

---

## 🚀 **Quick Fix Commands**

If you have the wrong path registered:

```batch
:: Remove bad scheduled task
schtasks /delete /tn "WindowSupportMonitor" /f

:: Remove bad Guardian service (if any)
sc stop WindowSupportGuardian
sc delete WindowSupportGuardian

:: Rebuild
PowerShell -ExecutionPolicy Bypass -File .\rebuild_all.ps1

:: Reinstall properly
:: Right-click INSTALL_WindowSupport.bat → Run as Administrator

:: Verify
schtasks /query /tn "WindowSupportMonitor" /v
```

---

## 📝 **Summary**

**What was fixed:**
- ✅ Location validation before startup registration
- ✅ Warning messages if run from wrong location
- ✅ Protection against registering incorrect paths
- ✅ Clear instructions for proper installation

**What you need to do:**
1. Rebuild with fixed code
2. Use installer (don't run from dist folder)
3. Verify scheduled task has correct path

**Result:**
- Application only registers when in correct location
- No more incorrect path registrations
- Clear user feedback about location issues

---

## 🎯 **Important Notes**

1. **Always use the installer** - Don't run exes directly from dist folder
2. **Installer handles everything** - Copies to correct location first
3. **Safe to test** - Running from dist won't break anything now (just shows warning)
4. **Easy to verify** - Check scheduled task path to confirm

---

**The bug is now fixed! Rebuild and reinstall to apply the fix.** ✨



