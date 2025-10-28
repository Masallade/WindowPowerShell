# WindowSupport - Complete Installation System

## 📦 What I Created for You

### **Main Files:**

1. **`INSTALL_WindowSupport.bat`** ⭐ **THE MAIN INSTALLER**
   - Complete automated installation script
   - Must run as Administrator
   - Does everything in one click!

2. **`rebuild_all.ps1`** (Updated)
   - Builds all executables
   - Now points to the installer

3. **Documentation:**
   - `INSTALLATION_GUIDE.md` - Complete detailed guide
   - `QUICK_START.txt` - Quick reference
   - `INSTALLER_FEATURES.md` - This file!

---

## ✨ Installer Features (All Your Requirements Met!)

### **✅ 1. Choose Which User to Install For**
```
Available users on this computer:
  1. Admin
  2. JohnDoe  
  3. JaneSmith

Enter the number: _
```
- Shows all users on the computer
- You select which user
- Installs to that user's AppData folder

### **✅ 2. Automatic Installation to AppData**
```
C:\Users\[SELECTED_USER]\AppData\Local\WindowSupport\
```
- Creates the directory automatically
- Copies all files (3 exe folders with dependencies)
- Sets correct permissions

### **✅ 3. Windows Defender Exclusions**
```powershell
Add-MpPreference -ExclusionPath 'C:\Users\...\WindowSupport'
Add-MpPreference -ExclusionProcess 'WindowPowerShellProvider.exe'
Add-MpPreference -ExclusionProcess 'WindowSupportGuardian.exe'
```
- Adds folder exclusion
- Adds process exclusions
- Prevents antivirus interference

### **✅ 4. Run get_your_staff_id.exe**
```
Launching Staff ID selector...
Please select your Staff ID in the window that opens.
```
- Automatically launches the Staff ID selector
- User picks their ID from dropdown
- Saves to registry and config file

### **✅ 5. 30-Second Wait**
```
Waiting 30 seconds for you to select your Staff ID...
[============================] 30s
```
- Gives user time to select and save Staff ID
- Shows countdown
- Proceeds automatically after 30 seconds

### **✅ 6. Run WindowPowerShellProvider.exe**
```
Starting WindowPowerShellProvider...
[OK] WindowPowerShellProvider started
[OK] Scheduled task created: WindowSupportMonitor
```
- Starts the main application
- Creates scheduled task for auto-start at login
- Task runs as the selected user
- Runs with highest privileges

### **✅ 7. Install WindowSupportGuardian as Service**
```
Installing WindowSupportGuardian as a Windows Service...
[OK] Service installed successfully
[OK] Guardian service started
```
- Installs as Windows Service
- Service name: `WindowSupportGuardian`
- Starts automatically
- Monitors and restarts Provider if it crashes
- Runs the service command: `WindowSupportGuardian.exe install`
- Then starts it: `WindowSupportGuardian.exe start`

---

## 🎯 Installation Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. Run INSTALL_WindowSupport.bat as Admin             │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  2. Check Admin Privileges                              │
│     ✓ Has admin? Continue                              │
│     ✗ No admin? Show error, exit                       │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  3. Show Users on Computer                              │
│     List all user profiles                              │
│     User selects by number                              │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  4. Copy Files                                           │
│     Source: dist\WindowSupport\                         │
│     Target: C:\Users\[USER]\AppData\Local\WindowSupport│
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  5. Add Windows Defender Exclusions                     │
│     - Folder exclusion                                  │
│     - Process exclusions (both exes)                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  6. Launch Staff ID Selector                            │
│     start get_your_staff_id.exe                        │
│     ⏰ Wait 30 seconds                                  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  7. Start Main Application                              │
│     - Create scheduled task                             │
│     - Start WindowPowerShellProvider.exe                │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  8. Install Guardian Service                            │
│     - WindowSupportGuardian.exe install                 │
│     - WindowSupportGuardian.exe start                   │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  9. Installation Complete!                              │
│     - Show summary                                      │
│     - Create uninstaller                                │
│     - All done! ✓                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 Commands Used Internally

### **For Defender Exclusions:**
```powershell
powershell -Command "Add-MpPreference -ExclusionPath '%TARGET_DIR%'"
powershell -Command "Add-MpPreference -ExclusionProcess 'WindowPowerShellProvider.exe'"
powershell -Command "Add-MpPreference -ExclusionProcess 'WindowSupportGuardian.exe'"
```

### **For Scheduled Task:**
```batch
schtasks /create /tn "WindowSupportMonitor" /tr "%EXE_PATH%" /sc onlogon /ru "%USER%" /rl highest /f
```

### **For Guardian Service:**
```batch
"%WindowSupportGuardian.exe%" install
"%WindowSupportGuardian.exe%" start
```

### **For Starting Provider:**
```batch
start "" "%WindowPowerShellProvider.exe%"
```

---

## 📁 Final File Structure

After installation:

```
C:\Users\[SELECTED_USER]\AppData\Local\WindowSupport\
├── WindowPowerShellProvider\
│   ├── WindowPowerShellProvider.exe     ← Main app
│   └── _internal\                        ← Dependencies
│       ├── python311.dll
│       ├── cv2 files
│       ├── PIL files
│       └── many other files
│
├── WindowSupportGuardian\
│   ├── WindowSupportGuardian.exe        ← Guardian service
│   └── _internal\                        ← Dependencies
│       └── service files
│
├── get_your_staff_id\
│   ├── get_your_staff_id.exe            ← Staff ID selector
│   └── _internal\                        ← Dependencies
│
├── app.log                               ← Application logs
├── error_logs.txt                        ← Error logs (hidden)
├── config.json                           ← Staff ID config
└── UNINSTALL.bat                         ← Auto-generated uninstaller
```

**Registry:**
```
HKEY_CURRENT_USER\Software\WindowSupport\
└── staff_id = "12345"
```

**Scheduled Task:**
- Name: `WindowSupportMonitor`
- Trigger: At user logon
- Run as: Selected user
- Elevated: Yes

**Windows Service:**
- Name: `WindowSupportGuardian`
- Display Name: `Window Support Guardian Service`
- Startup Type: Automatic
- Status: Running

---

## 🎬 Usage

### **Build + Install (Complete Process):**

```powershell
# Step 1: Build
PowerShell -ExecutionPolicy Bypass -File .\rebuild_all.ps1

# Step 2: Install (right-click → Run as Administrator)
INSTALL_WindowSupport.bat
```

### **What User Sees:**

1. **Admin check** - "Running with Administrator privileges ✓"
2. **User selection** - Choose user from list
3. **File copying** - Progress indicator
4. **Defender setup** - Adding exclusions
5. **Staff ID** - GUI window opens, select ID
6. **Wait 30s** - Countdown timer
7. **Starting app** - "WindowPowerShellProvider started ✓"
8. **Installing service** - "Guardian service started ✓"
9. **Complete!** - Summary and verification instructions

**Total time: ~2 minutes**

---

## 🗑️ Bonus: Auto-Generated Uninstaller

The installer creates `UNINSTALL.bat` that:
- Stops all processes
- Removes scheduled task
- Stops and removes service
- Removes Defender exclusions
- Shows instructions for manual file deletion

---

## 📊 Summary

| Your Requirement | How It's Implemented | Status |
|-----------------|---------------------|--------|
| 1. Choose user | Shows list, user selects by number | ✅ Done |
| 2. Install to AppData | Copies to C:\Users\[USER]\AppData\Local\WindowSupport | ✅ Done |
| 3. Defender exclusions | Adds path + process exclusions | ✅ Done |
| 4. Run Staff ID selector | Launches get_your_staff_id.exe | ✅ Done |
| 5. Wait 30 seconds | timeout /t 30 | ✅ Done |
| 6. Run main app | Starts WindowPowerShellProvider.exe + creates task | ✅ Done |
| 7. Run Guardian | Installs and starts as Windows Service | ✅ Done |

**ALL REQUIREMENTS MET!** ✨

---

## 🚀 Ready to Use!

Your complete installation system is ready:

1. ✅ Builds correctly (no crashes)
2. ✅ Installs to correct location
3. ✅ Configures everything automatically
4. ✅ Creates scheduled task
5. ✅ Installs Guardian service
6. ✅ Adds security exclusions
7. ✅ One-click installation
8. ✅ Creates uninstaller

**Just run the commands in QUICK_START.txt!**



