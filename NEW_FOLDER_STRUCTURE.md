# New Folder Structure After Fix

## 📁 How the Files are Organized Now

After rebuilding with the fixed `.spec` files, here's the new structure:

```
dist/
└── WindowSupport/
    ├── get_your_staff_id/                    ← Folder for staff ID selector
    │   ├── get_your_staff_id.exe             ← The executable
    │   └── _internal/                         ← All dependencies
    │       ├── python311.dll
    │       ├── base_library.zip
    │       └── [many other files]
    │
    ├── WindowPowerShellProvider/              ← Folder for main application
    │   ├── WindowPowerShellProvider.exe       ← The executable ⭐ MAIN APP
    │   └── _internal/                         ← All dependencies
    │       ├── python311.dll
    │       ├── cv2 files
    │       ├── PIL files
    │       └── [many other files]
    │
    ├── WindowSupportGuardian/                 ← Folder for guardian service
    │   ├── WindowSupportGuardian.exe          ← The executable
    │   └── _internal/                         ← All dependencies
    │       ├── python311.dll
    │       └── [other files]
    │
    └── Start_WindowSupport.bat                ← Quick launcher
```

---

## 🔗 How They Find Each Other

### **WindowSupportGuardian** needs to find **WindowPowerShellProvider**

The Guardian now searches in this order:

1. **Sibling folder** (most common):
   ```
   If Guardian is in: dist\WindowSupport\WindowSupportGuardian\
   It looks in:       dist\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe
   ```

2. **AppData folder**:
   ```
   %LOCALAPPDATA%\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe
   ```

3. **ProgramData folder**:
   ```
   %ProgramData%\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe
   ```

4. **Same directory** (backward compatibility)
5. **Old single-file location** (backward compatibility)

---

## 🎯 What Changed in the Code

### **WindowSupportGuardian.py**

**BEFORE** (assumed single .exe file):
```python
locations = [
    'C:\...\WindowSupport\WindowPowerShellProvider.exe',  # ❌ Won't find it!
]
```

**AFTER** (accounts for folder structure):
```python
guardian_dir = os.path.dirname(os.path.abspath(sys.executable))
parent_dir = os.path.dirname(guardian_dir)

locations = [
    # New: Look in sibling folder
    os.path.join(parent_dir, 'WindowPowerShellProvider', 'WindowPowerShellProvider.exe'),
    # Also check AppData with folder structure
    os.path.join(LOCALAPPDATA, 'WindowSupport', 'WindowPowerShellProvider', 'WindowPowerShellProvider.exe'),
    # ... etc
]
```

### **WindowPowerShellProvider.py**

✅ **No changes needed!** It uses `sys.executable` which automatically gets its own correct path.

---

## 📋 Path Examples

Let's say you install to: `D:\MyApps\WindowSupport\`

### Guardian's perspective:
```
My exe is at:     D:\MyApps\WindowSupport\WindowSupportGuardian\WindowSupportGuardian.exe
guardian_dir =    D:\MyApps\WindowSupport\WindowSupportGuardian\
parent_dir =      D:\MyApps\WindowSupport\
I'll look for:    D:\MyApps\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe
✅ Found it!
```

### Provider's perspective:
```
My exe is at:     D:\MyApps\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe
My _internal is:  D:\MyApps\WindowSupport\WindowPowerShellProvider\_internal\
✅ All dependencies found automatically!
```

---

## 🚀 How to Deploy

### **Option 1: Keep them together** (Recommended)
Copy the entire `WindowSupport` folder:
```
WindowSupport/
├── WindowPowerShellProvider/   ← Main app
├── WindowSupportGuardian/      ← Guardian (optional)
└── get_your_staff_id/          ← Setup tool
```

**Benefits:**
- Guardian can find Provider easily
- Everything stays organized
- Easy to backup/move

### **Option 2: Separate installation**
1. **Main app** → `%LOCALAPPDATA%\WindowSupport\WindowPowerShellProvider\`
2. **Guardian** → `%ProgramData%\WindowSupport\WindowSupportGuardian\`

**Note:** Make sure paths match what Guardian searches for!

---

## 🧪 Testing the Path Finding

### Test if Guardian can find Provider:

1. **Run Guardian exe**:
   ```
   dist\WindowSupport\WindowSupportGuardian\WindowSupportGuardian.exe install
   ```

2. **Check Event Log** (it will log which path it found):
   ```
   eventvwr.msc → Application logs
   Look for: "Found WindowPowerShellProvider at: [path]"
   ```

3. **Or check directly** with PowerShell:
   ```powershell
   # Get Guardian's location
   $guardianPath = "dist\WindowSupport\WindowSupportGuardian\WindowSupportGuardian.exe"
   $guardianDir = Split-Path $guardianPath
   $parentDir = Split-Path $guardianDir
   
   # Check if Provider exists at expected location
   $providerPath = Join-Path $parentDir "WindowPowerShellProvider\WindowPowerShellProvider.exe"
   Test-Path $providerPath  # Should return True
   ```

---

## ⚠️ Important Rules

### **DO:**
✅ Keep each exe with its `_internal` folder together
✅ Move the entire folder (exe + _internal) as one unit
✅ Keep both apps in the same parent directory if using Guardian

### **DON'T:**
❌ Separate the exe from its `_internal` folder
❌ Try to run the exe by itself without `_internal`
❌ Rename the `_internal` folder

---

## 🔄 Rebuild After Path Changes

Since we updated the Guardian's path search logic, you need to rebuild:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\rebuild_all.ps1
```

This will create new executables with the updated path-finding logic!

---

## 📝 Summary

| Aspect | Before (Broken) | After (Fixed) |
|--------|----------------|---------------|
| File structure | Single .exe | Folder with exe + _internal |
| Guardian finds Provider | ❌ Looks in wrong location | ✅ Checks multiple locations |
| Crash on startup | ❌ base_library.zip error | ✅ Runs smoothly |
| Path handling | Assumes single file | Smart folder-aware search |

---

## 🎯 Next Steps

1. ✅ **Rebuild** with: `.\rebuild_all.ps1`
2. ✅ **Test** Provider alone first
3. ✅ **Test** Guardian finding Provider
4. ✅ **Deploy** keeping folder structure intact



