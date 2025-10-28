# Window Support MSI Installer

## Prerequisites

1. **WiX Toolset v3.11 or later**
   - Download from: https://github.com/wixtoolset/wix3/releases
   - Install WiX Toolset
   - Verify installation: `$env:WIX` should point to WiX install directory

2. **Built EXE Files**
   - Ensure `dist\` folder contains:
     - `WindowPowerShellProvider.exe`
     - `WindowSupportGuardian.exe`
     - `get_your_staff_id.exe`

---

## Building the MSI

### Method 1: Automatic Build (Recommended)

```powershell
cd installer
.\build_msi.ps1
```

### Method 2: Manual Build

```powershell
cd installer

# Compile
candle.exe -nologo -ext WixUIExtension WindowSupport.wxs

# Link
light.exe -nologo -ext WixUIExtension -out WindowSupport.msi WindowSupport.wixobj -sval
```

---

## What the MSI Does

### During Installation:

1. **Copies files** to `%LOCALAPPDATA%\WindowSupport\`
   - WindowPowerShellProvider.exe
   - WindowSupportGuardian.exe
   - get_your_staff_id.exe

2. **Runs Staff ID Selector**
   - User selects their staff ID
   - Saves to registry

3. **Installs Guardian Service** (requires admin)
   - Creates Windows Service
   - Configures auto-start
   - Starts service

4. **Runs Main Provider**
   - Creates scheduled task with auto-restart
   - Starts monitoring

### During Uninstallation:

1. Stops and removes Guardian service
2. Removes scheduled task
3. Deletes all files
4. Cleans up registry entries

---

## Installing the MSI

### Interactive Install:
```powershell
msiexec /i WindowSupport.msi
```

Or just double-click `WindowSupport.msi`

### Silent Install:
```powershell
msiexec /i WindowSupport.msi /quiet /norestart
```

### Silent Install with Log:
```powershell
msiexec /i WindowSupport.msi /quiet /norestart /l*v install.log
```

---

## Uninstalling

### Via Control Panel:
1. Settings → Apps → Window Support Monitor → Uninstall

### Via Command Line:
```powershell
msiexec /x WindowSupport.msi /quiet
```

---

## Deployment via Group Policy (Enterprise)

1. Copy `WindowSupport.msi` to network share
2. Open Group Policy Management
3. Create/Edit GPO
4. Navigate to: Computer Configuration → Policies → Software Settings → Software Installation
5. Right-click → New → Package
6. Select `WindowSupport.msi`
7. Choose "Assigned" deployment
8. Apply to target OUs

---

## Troubleshooting

### "WiX not found" error:
- Install WiX Toolset
- Or specify path: `.\build_msi.ps1 -WixPath "C:\Path\To\WiX\bin"`

### "EXE not found" error:
- Build EXE files first using PyInstaller
- Ensure they're in `dist\` folder

### Installation fails:
- Check install log: `msiexec /i WindowSupport.msi /l*v install.log`
- Ensure admin rights for Guardian service install

### Guardian service not installing:
- Run MSI as administrator
- Or install service manually after: `WindowSupportGuardian.exe install`

---

## MSI Properties

| Property | Value |
|----------|-------|
| Name | Window Support Monitor |
| Version | 2.0.0 |
| Manufacturer | Window Support |
| Install Scope | Per-User |
| Install Location | %LOCALAPPDATA%\WindowSupport |
| Upgrade Code | 6D8C3A9A-3D47-4C0B-9F8C-5F4E9D7B2C11 |

---

## Files Included in MSI

```
WindowSupport\
  ├── WindowPowerShellProvider.exe  (Main monitoring app)
  ├── WindowSupportGuardian.exe     (Guardian service)
  └── get_your_staff_id.exe         (Staff ID selector)
```

---

## Version History

### v2.0.0
- Added Guardian service
- Improved crash resistance
- Multi-user support
- Auto-restart mechanisms

---

## Support

For issues or questions, check:
- Event Viewer → Windows Logs → Application (for Guardian logs)
- `%LOCALAPPDATA%\WindowSupport\app.log` (for main app logs)




