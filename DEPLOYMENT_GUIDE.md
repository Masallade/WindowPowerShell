# WindowPowerShellProvider - Deployment Guide

## 🚀 Complete Deployment Instructions

### Prerequisites
1. Python 3.8+ installed
2. Administrator access (one-time for antivirus exclusions)

---

## Step 1: Install Dependencies

```powershell
pip install pywin32 Pillow numpy opencv-python psutil requests cloudscraper certifi
python -m pywin32_postinstall -install
```

---

## Step 2: Build Executable

```powershell
# Install PyInstaller
pip install pyinstaller

# Build the EXE (no console window)
pyinstaller --onefile --noconsole --name WindowPowerShellProvider WindowPowerShellProvider.py
```

The EXE will be in `dist\WindowPowerShellProvider.exe`

---

## Step 3: Deploy to User AppData

```powershell
# Copy EXE to user's local AppData
$destination = "$env:LOCALAPPDATA\WindowSupport"
New-Item -ItemType Directory -Path $destination -Force
Copy-Item "dist\WindowPowerShellProvider.exe" -Destination $destination
```

---

## Step 4: Set Staff ID (Per User)

Each user must run `get_your_staff_id.py` once:

```powershell
python get_your_staff_id.py
```

This stores the staff ID in:
- Registry: `HKEY_CURRENT_USER\Software\WindowSupport`
- Fallback: `%LOCALAPPDATA%\WindowSupport\config.json`

---

## Step 5: Add Windows Defender Exclusions (CRITICAL)

### Automatic (Prompts for Admin):
Run the EXE once - it will attempt to add exclusions automatically.

### Manual (Recommended):
Run PowerShell **as Administrator**:

```powershell
# Add exclusions
Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\WindowSupport\WindowPowerShellProvider.exe"
Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\WindowSupport"
Add-MpPreference -ExclusionProcess "WindowPowerShellProvider.exe"

# Verify exclusions
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

### Helper Batch File:
After first run, a helper script is created at:
`%LOCALAPPDATA%\WindowSupport\add_exclusions.bat`

Right-click → **Run as Administrator**

---

## Step 6: First Run

```powershell
cd "$env:LOCALAPPDATA\WindowSupport"
.\WindowPowerShellProvider.exe
```

**On first run, it will:**
1. Set process priority to HIGH
2. Create scheduled task with auto-restart
3. Attempt to add Windows Defender exclusions
4. Start monitoring

---

## Step 7: Verify Installation

### Check Scheduled Task:
```powershell
schtasks /query /tn "WindowSupportMonitor" /fo LIST /v
```

### Check if Running:
```powershell
Get-Process -Name "WindowPowerShellProvider" -ErrorAction SilentlyContinue
```

### Check Logs:
```powershell
notepad "$env:LOCALAPPDATA\WindowSupport\app.log"
```

---

## 🛡️ Protection Features

### Scheduled Task Configuration:
- ✅ Auto-starts at user login
- ✅ Auto-restarts if stopped/crashed (999 times, 1-min interval)
- ✅ Runs with high priority
- ✅ Hidden from task list
- ✅ Highest available privileges
- ✅ Ignores new instances (prevents duplicates)

### Built-in Protection:
- ✅ Watchdog thread (restarts if stalled >5 min)
- ✅ Health checks every 10 iterations
- ✅ Auto-restart on 5 consecutive errors
- ✅ Memory cleanup (prevents leaks)
- ✅ Log rotation (prevents disk fill)
- ✅ Network connectivity checks

---

## 🔧 Troubleshooting

### Process Keeps Stopping After 2 Weeks?

1. **Check Windows Defender:**
   ```powershell
   Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
   ```
   If not listed, re-add exclusions.

2. **Check Other Antiviruses:**
   - Manually add to your AV's exclusion list
   - See vendor-specific instructions below

3. **Check Task Scheduler:**
   ```powershell
   Get-ScheduledTask -TaskName "WindowSupportMonitor" | Get-ScheduledTaskInfo
   ```

4. **Check Logs:**
   Look for crashes in: `%LOCALAPPDATA%\WindowSupport\app.log`

---

## 📋 Antivirus Exclusion Instructions

### Common Antiviruses:

**Avast/AVG:**
1. Settings → General → Exceptions
2. Add File Path: `%LOCALAPPDATA%\WindowSupport\WindowPowerShellProvider.exe`

**Norton:**
1. Settings → Antivirus → Scans and Risks → Exclusions
2. Add: Configure → Add Folders/Files

**McAfee:**
1. Real-Time Scanning → Excluded Files
2. Add File: Browse to EXE location

**Kaspersky:**
1. Settings → Additional → Threats and Exclusions
2. Manage Exclusions → Add

**Bitdefender:**
1. Protection → Antivirus → Settings (gear icon)
2. Manage Exceptions → Add an Exception

---

## 🌐 Multi-User Devices

### How It Works:
- Each user gets their own instance when they log in
- Each user has their own staff_id
- Screenshots capture only that user's screen
- Scheduled task is per-user, not system-wide

### Setup for Each User:
1. User logs in
2. Run `get_your_staff_id.py` (set their staff_id)
3. Run `WindowPowerShellProvider.exe` once
4. Done! Auto-starts on their next login

---

## 📊 Monitoring

### Real-time Status:
```powershell
# View current process
Get-Process -Name "WindowPowerShellProvider" | Format-List *

# View logs (live tail)
Get-Content "$env:LOCALAPPDATA\WindowSupport\app.log" -Tail 20 -Wait
```

### Memory Usage:
```powershell
Get-Process -Name "WindowPowerShellProvider" | Select-Object Name, @{Name="Memory(MB)";Expression={[math]::Round($_.WS/1MB,2)}}
```

---

## 🔄 Updating the EXE

1. Stop existing process:
   ```powershell
   Stop-Process -Name "WindowPowerShellProvider" -Force
   ```

2. Replace EXE in `%LOCALAPPDATA%\WindowSupport\`

3. Restart will happen automatically (scheduled task)

---

## ❌ Complete Uninstall

```powershell
# Stop process
Stop-Process -Name "WindowPowerShellProvider" -Force -ErrorAction SilentlyContinue

# Delete scheduled task
schtasks /delete /tn "WindowSupportMonitor" /f

# Remove files
Remove-Item "$env:LOCALAPPDATA\WindowSupport" -Recurse -Force

# Remove registry entry
Remove-Item "HKCU:\Software\WindowSupport" -Recurse -Force -ErrorAction SilentlyContinue

# Remove Windows Defender exclusions (as Admin)
Remove-MpPreference -ExclusionPath "$env:LOCALAPPDATA\WindowSupport\WindowPowerShellProvider.exe"
Remove-MpPreference -ExclusionPath "$env:LOCALAPPDATA\WindowSupport"
Remove-MpPreference -ExclusionProcess "WindowPowerShellProvider.exe"
```

---

## 📞 Support

### Log Locations:
- Main log: `%LOCALAPPDATA%\WindowSupport\app.log`
- Error log: `%LOCALAPPDATA%\WindowSupport\error_logs.txt`
- Config: `%LOCALAPPDATA%\WindowSupport\config.json`

### Common Issues:

**"Staff ID not found"**
→ Run `get_your_staff_id.py` to set staff ID

**"No network connectivity"**
→ Check firewall/proxy settings

**High memory usage**
→ App auto-restarts if >500MB, check logs for issues

---

## ✅ Production Checklist

- [ ] Dependencies installed
- [ ] EXE built with `--noconsole` flag
- [ ] Deployed to `%LOCALAPPDATA%\WindowSupport\`
- [ ] Staff ID set (registry or config.json)
- [ ] Windows Defender exclusions added
- [ ] Other AV exclusions added (if applicable)
- [ ] First run successful
- [ ] Scheduled task created
- [ ] Process visible in Task Manager
- [ ] Logs being generated
- [ ] Screenshots being sent to API

---

**Version:** 1.0  
**Last Updated:** 2025-10-21


