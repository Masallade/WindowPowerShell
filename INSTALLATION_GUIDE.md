# WindowSupport - Complete Installation Guide

## 🚀 Quick Start

### **Step 1: Build the Executables**
```powershell
PowerShell -ExecutionPolicy Bypass -File .\rebuild_all.ps1
```
Wait for it to complete (you'll see "BUILD COMPLETED SUCCESSFULLY!")

### **Step 2: Run the Installer**
1. Right-click on `INSTALL_WindowSupport.bat`
2. Select **"Run as Administrator"**
3. Follow the on-screen prompts

---

## 📋 What the Installer Does

### **Automatic Installation Process:**

1. ✅ **Checks Admin Privileges** - Ensures you have permissions
2. ✅ **Shows Available Users** - Lists all users on the computer
3. ✅ **Lets You Choose** - You select which user to install for
4. ✅ **Copies Files** - Installs to `C:\Users\[USER]\AppData\Local\WindowSupport`
5. ✅ **Adds Security Exclusions** - Adds to Windows Defender exclusions
6. ✅ **Configures Staff ID** - Launches the staff ID selector (30 second timer)
7. ✅ **Starts Main App** - Runs WindowPowerShellProvider.exe
8. ✅ **Creates Scheduled Task** - Auto-start at user login
9. ✅ **Installs Guardian Service** - Monitors and restarts if needed
10. ✅ **Creates Uninstaller** - For easy removal later

---

## 🎯 Step-by-Step Instructions

### **Before Installation:**

1. **Build the executables first:**
   ```powershell
   PowerShell -ExecutionPolicy Bypass -File .\rebuild_all.ps1
   ```

2. **Verify the build:**
   - Check that `dist\WindowSupport\` folder exists
   - Should contain 3 subfolders (one for each exe)

### **During Installation:**

#### **Screen 1: Admin Check**
```
Running with Administrator privileges? ✓
```
If you see an error, right-click the .bat file and choose "Run as Administrator"

#### **Screen 2: User Selection**
```
Available users on this computer:
  1. Admin
  2. JohnDoe
  3. JaneSmith
  
Enter the number of the user to install for: _
```
**Type the number** of the user you want to install for (e.g., type `2` for JohnDoe)

#### **Screen 3: File Copying**
```
Copying WindowSupport files...
[OK] Files copied successfully
```
Files are being copied to: `C:\Users\[USER]\AppData\Local\WindowSupport\`

#### **Screen 4: Defender Exclusions**
```
Adding Windows Defender Exclusions...
[OK] Folder exclusion added
[OK] Process exclusion added
```
This prevents antivirus from blocking the application

#### **Screen 5: Staff ID Selection**
```
Launching Staff ID selector...
Please select your Staff ID in the window that opens.
Waiting 30 seconds...
```
**ACTION REQUIRED:** A window will pop up - **select your Staff ID and click Save**

#### **Screen 6: Starting Application**
```
Starting WindowPowerShellProvider...
[OK] Scheduled task created
[OK] WindowPowerShellProvider started
```
The main application is now running!

#### **Screen 7: Guardian Service**
```
Installing WindowSupportGuardian as a Windows Service...
[OK] Service installed successfully
[OK] Guardian service started
```
Guardian will monitor and restart the app if it stops

#### **Screen 8: Complete!**
```
INSTALLATION COMPLETED SUCCESSFULLY!
```
Everything is set up and running!

---

## ✅ Verification

After installation, verify everything is working:

### **1. Check Scheduled Task**
```powershell
schtasks /query /tn "WindowSupportMonitor"
```
Should show: Status = Ready

### **2. Check Guardian Service**
```powershell
sc query WindowSupportGuardian
```
Should show: STATE = RUNNING

### **3. Check Process**
```powershell
Get-Process WindowPowerShellProvider
```
Should show the running process

### **4. Check Logs**
```
C:\Users\[USER]\AppData\Local\WindowSupport\app.log
```
Should contain startup messages

---

## 📂 Installation Locations

### **Files are installed to:**
```
C:\Users\[USER]\AppData\Local\WindowSupport\
├── WindowPowerShellProvider\
│   ├── WindowPowerShellProvider.exe
│   └── _internal\
├── WindowSupportGuardian\
│   ├── WindowSupportGuardian.exe
│   └── _internal\
├── get_your_staff_id\
│   ├── get_your_staff_id.exe
│   └── _internal\
├── app.log                    ← Application logs
├── error_logs.txt             ← Error logs
├── config.json                ← Staff ID config
└── UNINSTALL.bat              ← Uninstaller
```

### **Registry:**
- Staff ID stored in: `HKEY_CURRENT_USER\Software\WindowSupport`

### **Scheduled Task:**
- Task Name: `WindowSupportMonitor`
- Location: Task Scheduler Library

### **Windows Service:**
- Service Name: `WindowSupportGuardian`
- Display Name: `Window Support Guardian Service`

---

## 🔧 Troubleshooting

### **Problem: "This script requires Administrator privileges"**
**Solution:** Right-click the .bat file and select "Run as Administrator"

### **Problem: "Source directory not found"**
**Solution:** Build the executables first:
```powershell
PowerShell -ExecutionPolicy Bypass -File .\rebuild_all.ps1
```

### **Problem: "Could not add folder exclusion"**
**Solution:** 
- Windows Defender may be managed by organization policy
- Not critical - app will still work, but may be slower
- Manually add exclusion in Windows Security settings

### **Problem: "Service installation failed"**
**Solution:** 
- The app will still work via scheduled task
- Guardian provides extra monitoring, but isn't required
- Check if another service with same name exists

### **Problem: Staff ID window didn't appear**
**Solution:** 
- Manually run: `C:\Users\[USER]\AppData\Local\WindowSupport\get_your_staff_id\get_your_staff_id.exe`
- Select your Staff ID
- Save and close

### **Problem: Application not starting at login**
**Solution:** Check scheduled task:
```powershell
schtasks /query /tn "WindowSupportMonitor" /v
```
Look for errors in the task properties

---

## 🗑️ Uninstallation

### **Easy Method:**
Run the uninstaller created during installation:
```
C:\Users\[USER]\AppData\Local\WindowSupport\UNINSTALL.bat
```
Right-click and **"Run as Administrator"**

### **Manual Method:**

1. **Stop processes:**
   ```powershell
   taskkill /F /IM WindowPowerShellProvider.exe
   taskkill /F /IM WindowSupportGuardian.exe
   ```

2. **Remove scheduled task:**
   ```powershell
   schtasks /delete /tn "WindowSupportMonitor" /f
   ```

3. **Stop and remove service:**
   ```powershell
   sc stop WindowSupportGuardian
   sc delete WindowSupportGuardian
   ```

4. **Remove Defender exclusions:**
   ```powershell
   powershell -Command "Remove-MpPreference -ExclusionPath 'C:\Users\[USER]\AppData\Local\WindowSupport'"
   powershell -Command "Remove-MpPreference -ExclusionProcess 'WindowPowerShellProvider.exe'"
   ```

5. **Delete files:**
   ```
   C:\Users\[USER]\AppData\Local\WindowSupport\
   ```

---

## 🎯 Summary

| Step | What Happens | Time |
|------|-------------|------|
| 1. Build | Compile Python to EXE | 2-5 min |
| 2. Install | Run INSTALL_WindowSupport.bat | 2 min |
| 3. Configure | Select Staff ID | 30 sec |
| 4. Verify | Check it's running | 1 min |

**Total time: ~5-10 minutes**

---

## 📞 Support

If you encounter issues:
1. Check the logs: `C:\Users\[USER]\AppData\Local\WindowSupport\app.log`
2. Check error logs: `C:\Users\[USER]\AppData\Local\WindowSupport\error_logs.txt`
3. Verify scheduled task: `taskschd.msc`
4. Check services: `services.msc`

---

## ⚙️ Advanced: Silent Installation

For IT admins deploying to multiple computers:

```batch
:: Build first
PowerShell -ExecutionPolicy Bypass -File .\rebuild_all.ps1

:: Then modify INSTALL_WindowSupport.bat to accept parameters
:: Or use Group Policy to deploy scheduled task and service
```

---

## 🎉 Success Indicators

Everything is working correctly if:

✅ No crash when running any .exe  
✅ Scheduled task "WindowSupportMonitor" exists and is Ready  
✅ Service "WindowSupportGuardian" is Running  
✅ Process "WindowPowerShellProvider.exe" is in Task Manager  
✅ Logs are being written to app.log  
✅ No errors in error_logs.txt  
✅ Application restarts automatically after reboot  

---

**Your one-click installation is ready!** 🚀



