# Fix Summary - WindowSupport Startup & Crash Issues

## Issues Fixed

### 1. **PyInstaller Crash** ❌ → ✅
**Problem:** The executable was crashing with:
```
Failed to execute script 'WindowPowerShellProvider' due to unhandled exception: 
[Errno 2] No such file or directory: 
'C:\Users\...\AppData\Local\Temp\_MEI95362\base_library.zip'
```

**Root Cause:** The `.spec` files were configured to use `--onefile` mode, which bundles everything into a single executable. This mode extracts files to a temporary directory at runtime, which can cause issues with:
- Antivirus software blocking extraction
- Permission issues in temp directories
- Resource loading failures

**Solution:** Changed all three `.spec` files to use `--onedir` mode:
- `get_your_staff_id.spec`
- `WindowPowerShellProvider.spec`
- `WindowSupportGuardian.spec`

The key change in each file:
```python
# OLD (--onefile mode - causes crashes)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # ← Everything bundled into one exe
    a.datas,
    [],
    name='WindowPowerShellProvider',
    ...
)

# NEW (--onedir mode - stable and reliable)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # ← Keep binaries separate
    name='WindowPowerShellProvider',
    ...
)
coll = COLLECT(  # ← Create a directory with all dependencies
    exe,
    a.binaries,
    a.datas,
    ...
)
```

### 2. **Startup Registration Not Working** ❌ → ✅
**Problem:** The executable wasn't adding itself to Windows startup.

**Root Cause:** The original code used XML-based scheduled task creation which can fail due to:
- User account format issues (DOMAIN\User vs just User)
- XML encoding problems
- Silent failures without proper error reporting

**Solution:** Rewrote `add_to_startup()` function in `WindowPowerShellProvider.py`:
1. **Simplified Task Creation**: Uses direct `schtasks` command instead of XML
2. **Better Error Reporting**: Shows all error messages and return codes
3. **Fallback Method**: If scheduled task fails, creates a startup folder shortcut
4. **Verification**: Checks if task was created successfully

Key improvements:
```python
# Simplified command that works reliably
create_cmd = f'schtasks /create /tn "{task_name}" /tr "\"{exe_path}\"" /sc onlogon /rl highest /f'

# Detailed logging
print(f"Create task return code: {result.returncode}")
print(f"Create task stdout: {result.stdout}")
if result.stderr:
    print(f"Create task stderr: {result.stderr}")

# Fallback to startup folder if task creation fails
if result.returncode != 0:
    # Creates .lnk file in Startup folder as backup
```

## How to Rebuild

### Option 1: Use the PowerShell Script (Recommended)
```powershell
.\rebuild_all.ps1
```

This script will:
1. Clean old builds
2. Build all three executables
3. Organize them in `dist\WindowSupport\`
4. Create a launcher batch file

### Option 2: Manual Build
```powershell
# Clean previous builds
Remove-Item -Recurse -Force build, dist

# Build each component
pyinstaller get_your_staff_id.spec --clean
pyinstaller WindowPowerShellProvider.spec --clean
pyinstaller WindowSupportGuardian.spec --clean
```

## Testing the Fixes

### 1. Test for Crashes
```powershell
# Navigate to the built directory
cd dist\WindowSupport\WindowPowerShellProvider

# Run the executable
.\WindowPowerShellProvider.exe
```

**Expected Result:** 
- No crash
- Console window appears briefly (or hidden if console=False)
- Application runs in background
- Check logs in: `%LOCALAPPDATA%\WindowSupport\app.log`

### 2. Test Startup Registration
After running the executable:

**Check Scheduled Task:**
```powershell
schtasks /query /tn "WindowSupportMonitor"
```

**Expected Output:**
```
Folder: \
TaskName                                 Next Run Time          Status
======================================== ====================== ===============
WindowSupportMonitor                     At log on              Ready
```

**Check Startup Folder (Fallback):**
```powershell
dir "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\WindowSupport.lnk"
```

### 3. Test Auto-Start
1. Restart your computer
2. Log in
3. Check if the process is running:
```powershell
Get-Process WindowPowerShellProvider
```

## File Structure After Build

```
dist/
└── WindowSupport/
    ├── get_your_staff_id/
    │   ├── get_your_staff_id.exe
    │   └── [dependencies]
    ├── WindowPowerShellProvider/
    │   ├── WindowPowerShellProvider.exe
    │   └── [dependencies including CV2, PIL, etc.]
    ├── WindowSupportGuardian/
    │   ├── WindowSupportGuardian.exe
    │   └── [dependencies]
    └── Start_WindowSupport.bat
```

## Key Differences: --onefile vs --onedir

| Aspect | --onefile (OLD) | --onedir (NEW) |
|--------|----------------|----------------|
| File Structure | Single .exe | Directory with .exe + dependencies |
| Startup Speed | Slower (extract to temp) | Faster (files already on disk) |
| Antivirus Issues | Common (unpacking detected as suspicious) | Rare |
| Debugging | Harder (temp extraction) | Easier (persistent files) |
| Crashes | More common | Much more stable |
| Distribution | Simpler (1 file) | Slightly more complex (1 folder) |

## Why This Fix Works

1. **No Temp Directory Extraction**: Files are already on disk, no runtime extraction needed
2. **Better Permissions**: User has full control over the install directory
3. **Antivirus Friendly**: No runtime unpacking that triggers heuristic detection
4. **Easier Debugging**: All dependencies visible on disk
5. **Reliable Startup**: Simplified command works across different Windows configurations

## Logs Location

Monitor these files to troubleshoot issues:
- `%LOCALAPPDATA%\WindowSupport\app.log` - Application logs
- `%LOCALAPPDATA%\WindowSupport\error_logs.txt` - Error logs
- Event Viewer → Windows Logs → Application - Scheduled Task events

## Additional Notes

- The executable will now print detailed debug information
- The scheduled task is set to "highest" privileges (requires UAC prompt on first run)
- The application logs all startup attempts and errors
- If scheduled task fails, it automatically falls back to startup folder shortcut

## Rollback

If you need to rollback to the old configuration:
1. Delete the `COLLECT` section from each `.spec` file
2. Change `exclude_binaries=True` back to include all binaries in EXE
3. Rebuild

## Support

If issues persist:
1. Check logs in `%LOCALAPPDATA%\WindowSupport\`
2. Run in console mode to see live output:
   - Change `console=False` to `console=True` in `.spec` files
   - Rebuild
3. Verify Task Scheduler: `taskschd.msc`



