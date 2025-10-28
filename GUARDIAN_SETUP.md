# WindowSupport Guardian - Setup Guide

## 🛡️ What is the Guardian?

The Guardian is a secondary monitoring process that ensures `WindowPowerShellProvider.exe` is always running. It provides an extra layer of protection.

**Guardian Architecture:**
```
Windows Service (Guardian)
    ↓ (monitors every 30 seconds)
WindowPowerShellProvider.exe
    ↓ (monitors user activity)
API Server
```

---

## 📋 Two Options Available

### **Option 1: Python Service (Recommended)**
- Runs as Windows Service
- System-level protection
- Auto-starts with Windows
- More robust

### **Option 2: Batch File (Simple)**
- Runs as scheduled task
- Easier to setup
- No Python service dependencies
- Good for testing

---

## 🚀 Option 1: Python Service Setup

### Step 1: Install Additional Dependencies
```powershell
pip install pywin32 psutil
```

### Step 2: Install the Service

**Run PowerShell as Administrator:**

```powershell
# Install the service
python WindowSupportGuardian.py install

# Start the service
python WindowSupportGuardian.py start

# Verify it's running
Get-Service -Name "WindowSupportGuardian"
```

### Step 3: Configure Auto-Start

```powershell
# Set service to start automatically
sc config WindowSupportGuardian start= auto

# Verify configuration
sc qc WindowSupportGuardian
```

### Service Management Commands:

```powershell
# Start service
python WindowSupportGuardian.py start
# OR
net start WindowSupportGuardian

# Stop service
python WindowSupportGuardian.py stop
# OR
net stop WindowSupportGuardian

# Restart service
python WindowSupportGuardian.py restart

# Remove service
python WindowSupportGuardian.py remove
```

### View Service Logs:

Open **Event Viewer** → **Windows Logs** → **Application**

Look for events from: `WindowSupportGuardian`

---

## 🚀 Option 2: Batch File Setup (Simpler)

### Step 1: Create Scheduled Task

**Run PowerShell as Administrator:**

```powershell
# Create the task
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$env:LOCALAPPDATA\WindowSupport\WindowSupportGuardian.bat`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Days 365)

Register-ScheduledTask -TaskName "WindowSupportGuardian" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Monitors and restarts WindowPowerShellProvider"

# Start the task immediately
Start-ScheduledTask -TaskName "WindowSupportGuardian"
```

### Step 2: Verify It's Running

```powershell
# Check task status
Get-ScheduledTask -TaskName "WindowSupportGuardian" | Get-ScheduledTaskInfo

# Check if CMD process is running the batch file
Get-Process -Name "cmd" | Where-Object {$_.CommandLine -like "*WindowSupportGuardian.bat*"}
```

### Stop the Guardian:

```powershell
Stop-ScheduledTask -TaskName "WindowSupportGuardian"
```

---

## 📊 How It Works

### Python Service Version:
1. Runs as Windows Service (system-level)
2. Checks every 30 seconds if `WindowPowerShellProvider.exe` is running
3. If not running and user is logged in:
   - Tries to start via scheduled task (preferred)
   - Falls back to direct start if task doesn't exist
4. Logs all actions to Windows Event Log

### Batch File Version:
1. Runs continuously via scheduled task
2. Checks every 30 seconds using `tasklist`
3. If process not found:
   - Tries scheduled task first
   - Falls back to direct start
4. Logs to console (captured by Task Scheduler)

---

## 🔍 Monitoring the Guardian

### Python Service:

**Check service status:**
```powershell
Get-Service -Name "WindowSupportGuardian" | Format-List *
```

**View logs:**
```powershell
Get-EventLog -LogName Application -Source "WindowSupportGuardian" -Newest 20
```

### Batch File:

**Check if running:**
```powershell
Get-ScheduledTask -TaskName "WindowSupportGuardian" | Get-ScheduledTaskInfo
```

**View task history:**
1. Open Task Scheduler (`taskschd.msc`)
2. Find "WindowSupportGuardian"
3. Click "History" tab

---

## ⚖️ Which Option to Choose?

### Use **Python Service** if:
- ✅ You want maximum reliability
- ✅ You need system-level monitoring
- ✅ You're comfortable with Windows Services
- ✅ You want Event Log integration

### Use **Batch File** if:
- ✅ You want simple setup
- ✅ You're testing the concept
- ✅ You don't need system service complexity
- ✅ You prefer scheduled tasks over services

---

## 🎯 Recommended Setup (Maximum Protection)

**Best practice: Use BOTH layers:**

1. **Primary:** Scheduled Task (per-user, auto-restart)
   - Created by `WindowPowerShellProvider.exe` on first run
   - Restarts 999 times if crashed

2. **Secondary:** Guardian Service (system-level watchdog)
   - Monitors if primary fails
   - Restarts main EXE if stopped

**Protection Layers:**
```
Layer 1: WindowPowerShellProvider.exe (built-in watchdog thread)
Layer 2: Scheduled Task (auto-restart on failure)
Layer 3: Guardian Service (external monitor)
```

---

## 🔧 Troubleshooting

### Python Service Won't Start:

1. **Check if pywin32 is installed:**
   ```powershell
   python -c "import win32serviceutil; print('OK')"
   ```

2. **Check service logs:**
   ```powershell
   Get-EventLog -LogName Application -Source "WindowSupportGuardian" -Newest 5
   ```

3. **Reinstall service:**
   ```powershell
   python WindowSupportGuardian.py remove
   python WindowSupportGuardian.py install
   python WindowSupportGuardian.py start
   ```

### Batch File Not Working:

1. **Check if task exists:**
   ```powershell
   Get-ScheduledTask -TaskName "WindowSupportGuardian"
   ```

2. **Check batch file path:**
   ```powershell
   Test-Path "$env:LOCALAPPDATA\WindowSupport\WindowSupportGuardian.bat"
   ```

3. **Run manually to test:**
   ```powershell
   cmd /c "$env:LOCALAPPDATA\WindowSupport\WindowSupportGuardian.bat"
   ```

### Guardian Running but Not Restarting Main EXE:

1. **Check EXE path in guardian**
2. **Verify scheduled task "WindowSupportMonitor" exists**
3. **Check Event Logs for errors**
4. **Ensure user is logged in (guardian needs active session)**

---

## 🗑️ Uninstall Guardian

### Python Service:
```powershell
# Stop and remove service
python WindowSupportGuardian.py stop
python WindowSupportGuardian.py remove
```

### Batch File:
```powershell
# Stop and delete task
Stop-ScheduledTask -TaskName "WindowSupportGuardian"
Unregister-ScheduledTask -TaskName "WindowSupportGuardian" -Confirm:$false
```

---

## 📝 Configuration Options

### Change Check Interval:

**Python Service:**
Edit `WindowSupportGuardian.py`, line ~114:
```python
check_interval = 30  # Change to desired seconds
```
Then reinstall service.

**Batch File:**
Edit `WindowSupportGuardian.bat`, line ~7:
```batch
set "CHECK_INTERVAL=30"
```

### Change EXE Location:

**Python Service:**
Edit `WindowSupportGuardian.py`, line ~83-87 (locations list)

**Batch File:**
Edit `WindowSupportGuardian.bat`, line ~10:
```batch
set "EXE_PATH=C:\Your\Custom\Path\WindowPowerShellProvider.exe"
```

---

## ✅ Deployment Checklist

- [ ] Choose Guardian option (Service or Batch)
- [ ] Install dependencies (if using Python Service)
- [ ] Copy guardian files to deployment location
- [ ] Install/Configure guardian (as Administrator)
- [ ] Verify guardian is running
- [ ] Test by manually stopping main EXE
- [ ] Verify guardian restarts main EXE within 30 seconds
- [ ] Check logs/event viewer
- [ ] Reboot and verify auto-start

---

**Note:** The Guardian is optional but highly recommended for mission-critical deployments where maximum uptime is required.

---

**Version:** 1.0  
**Last Updated:** 2025-10-21



