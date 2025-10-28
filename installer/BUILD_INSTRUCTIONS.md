# How to Build the MSI Installer

## ⚠️ WiX Toolset Required

The MSI installer needs WiX Toolset to build.

---

## Step 1: Install WiX Toolset

1. Download **WiX Toolset v3.11.2** from:
   - https://github.com/wixtoolset/wix3/releases/download/wix3112rtm/wix311.exe

2. Run the installer

3. Verify installation:
   ```powershell
   $env:WIX
   ```
   Should output: `C:\Program Files (x86)\WiX Toolset v3.11\`

---

## Step 2: Build the MSI

### Option A: Use Simple Script (Recommended)

```powershell
cd installer
powershell -ExecutionPolicy Bypass .\build_msi_simple.ps1
```

### Option B: Manual Build

```powershell
cd installer

# Compile WiX source
"C:\Program Files (x86)\WiX Toolset v3.11\bin\candle.exe" -nologo -ext WixUIExtension WindowSupport.wxs

# Link to MSI
"C:\Program Files (x86)\WiX Toolset v3.11\bin\light.exe" -nologo -ext WixUIExtension -out WindowSupport.msi WindowSupport.wixobj -sval
```

---

## Step 3: Test the MSI

```powershell
# Install
msiexec /i WindowSupport.msi /l*v install.log

# Check logs if issues
notepad install.log
```

---

## What You'll Get

After building, you'll have:
- **WindowSupport.msi** (ready to deploy)

Size: ~50-100 MB (includes all 3 EXE files)

---

## Alternative: Use Advanced Installer (No WiX Needed)

If you don't want to install WiX, use **Advanced Installer**:

1. Download free version: https://www.advancedinstaller.com/
2. Create new project → Simple
3. Add files:
   - `dist\WindowPowerShellProvider.exe`
   - `dist\WindowSupportGuardian.exe`
   - `dist\get_your_staff_id.exe`
4. Set install location: `[LocalAppDataFolder]\WindowSupport`
5. Add custom actions:
   - Run `get_your_staff_id.exe` after install
   - Run `WindowSupportGuardian.exe install` (as admin)
   - Run `WindowPowerShellProvider.exe` once
6. Build → MSI created!

---

## Deployment

Once you have the MSI, you can:

### Single PC:
```powershell
msiexec /i WindowSupport.msi
```

### Multiple PCs (Silent):
```powershell
msiexec /i WindowSupport.msi /quiet /norestart
```

### Group Policy (Domain):
1. Copy MSI to network share
2. GPO → Software Installation → Assign
3. Apply to OUs

---

## Troubleshooting

**"WiX not found"**
- Install WiX Toolset from link above
- Or use Advanced Installer instead

**"EXE not found"**
- Build EXE files first with PyInstaller
- They must be in `dist\` folder

**Build fails**
- Check if dist\ has all 3 EXE files
- Make sure WiX is in PATH
- Try manual build commands above

---

**For quick deployment without MSI, see the simple manual deployment guide in main README.**




