# Quick Test Guide

## Step 1: Rebuild the Executables

Open PowerShell in this directory and run:

```powershell
.\rebuild_all.ps1
```

Wait for the build to complete (it will show green checkmarks ✓).

## Step 2: Test the First Executable (Staff ID Selector)

```powershell
cd dist\WindowSupport\get_your_staff_id
.\get_your_staff_id.exe
```

**What should happen:**
- A GUI window opens
- You can select your staff ID
- Click "Save and Exit"
- Window closes without errors

## Step 3: Test the Main Executable (Provider)

```powershell
cd ..\WindowPowerShellProvider
.\WindowPowerShellProvider.exe
```

**What should happen:**
- No crash! (This was the main issue)
- If you see a console window, you'll see startup messages
- After a few seconds, the console disappears (or minimizes)

## Step 4: Check if Startup Registration Worked

### Method 1: Check Scheduled Task
```powershell
schtasks /query /tn "WindowSupportMonitor" /v
```

**Expected output:** Task details showing it's ready to run at logon

### Method 2: Open Task Scheduler GUI
```powershell
taskschd.msc
```

Look for "WindowSupportMonitor" in the task list. It should show:
- Status: Ready
- Trigger: At log on
- Last Run Time: (the time you just ran it)

### Method 3: Check Startup Folder (if task failed)
```powershell
dir "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\"
```

Look for `WindowSupport.lnk` (only exists if scheduled task creation failed)

## Step 5: Check if Process is Running

```powershell
Get-Process WindowPowerShellProvider -ErrorAction SilentlyContinue
```

**If running:** Shows process details
**If not running:** No output (which means it finished or crashed)

## Step 6: Check Logs

```powershell
# View application log
notepad "$env:LOCALAPPDATA\WindowSupport\app.log"

# View error log (if any)
notepad "$env:LOCALAPPDATA\WindowSupport\error_logs.txt"
```

**Look for:**
- "✓ Scheduled task created successfully!" 
- "✓ Task verified successfully!"
- Any error messages

## Step 7: Test Auto-Restart at Login

### Option A: Restart Computer (full test)
```powershell
Restart-Computer
```

After login, check if process started automatically:
```powershell
Get-Process WindowPowerShellProvider
```

### Option B: Manually Trigger Task (quick test)
```powershell
schtasks /run /tn "WindowSupportMonitor"
```

Then check if it's running:
```powershell
Get-Process WindowPowerShellProvider
```

## Troubleshooting

### Issue: "PyInstaller not found"
```powershell
pip install pyinstaller
```

### Issue: "Access denied" when creating task
- Run PowerShell as Administrator
- Or accept the UAC prompt when it appears

### Issue: Task created but process doesn't start
```powershell
# Check task history
Get-ScheduledTaskInfo -TaskName "WindowSupportMonitor"

# Run task manually to see errors
schtasks /run /tn "WindowSupportMonitor"
```

### Issue: Still crashes with base_library.zip error
This means the rebuild didn't work. Try:
```powershell
# Clean everything
Remove-Item -Recurse -Force build, dist

# Rebuild manually
pyinstaller WindowPowerShellProvider.spec --clean --noconfirm
```

### Issue: Console window stays open
This is actually good for debugging! You can see what's happening. To hide it:
1. Open the `.spec` file
2. Change `console=False` (it should already be False)
3. Rebuild

## Success Indicators

✅ **Everything is working if:**
1. No crash when running the exe
2. Task "WindowSupportMonitor" exists in Task Scheduler
3. Task status shows "Ready"
4. Process starts automatically after reboot
5. Logs show "✓ Scheduled task created successfully!"

## Debug Mode (if issues persist)

To see detailed output:

1. Edit the `.spec` file:
```python
console=True,  # Change from False to True
```

2. Rebuild:
```powershell
pyinstaller WindowPowerShellProvider.spec --clean
```

3. Run and watch the console:
```powershell
.\dist\WindowPowerShellProvider\WindowPowerShellProvider.exe
```

The console will show exactly what's happening and any errors.

## Quick Command Reference

```powershell
# Rebuild all
.\rebuild_all.ps1

# Check if process running
Get-Process WindowPowerShellProvider

# Check scheduled task
schtasks /query /tn "WindowSupportMonitor"

# View logs
notepad "$env:LOCALAPPDATA\WindowSupport\app.log"

# Kill process (if needed)
Stop-Process -Name WindowPowerShellProvider -Force

# Delete scheduled task (if needed)
schtasks /delete /tn "WindowSupportMonitor" /f

# Start task manually
schtasks /run /tn "WindowSupportMonitor"
```

## Expected Behavior After Fixes

| What | Before (Broken) | After (Fixed) |
|------|----------------|---------------|
| Running exe | Crashes immediately | Runs successfully |
| Startup registration | Silent failure | Shows detailed status |
| Task Scheduler | No task created | Task created and verified |
| Auto-start | Doesn't start | Starts automatically |
| Error messages | Generic/none | Detailed and helpful |
| Distribution | Single .exe | Folder with .exe + dependencies |

## Next Steps After Successful Test

1. ✅ Executables are working
2. ✅ Startup registration works
3. ✅ Auto-start confirmed

You can now:
- Distribute the `dist\WindowSupport\` folder
- Create an installer (see `installer\` directory)
- Deploy to other machines

Remember: Each user needs to:
1. Run `get_your_staff_id.exe` first (one time)
2. Then run `WindowPowerShellProvider.exe` (will auto-register for startup)



