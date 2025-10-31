# OpenCV DLL Import Error - Fix Guide

## Problem

You're seeing this error:
```
ImportError: DLL load failed while importing cv2: The specified module could not be found.
```

This happens because OpenCV (cv2) requires **Visual C++ Redistributables** to be installed on the Windows system.

## Why It Works on Some Computers But Not Others

- **Computers where it works**: Already have Visual C++ Redistributables installed (usually installed automatically by other software like games, Adobe software, etc.)
- **Computers where it fails**: Don't have the required Visual C++ Redistributables installed

## Solutions

### Solution 1: Install Visual C++ Redistributables (Recommended)

Download and install the **Microsoft Visual C++ Redistributable for Visual Studio 2015-2022**:

**For 64-bit Windows:**
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Or search for "Visual C++ Redistributable 2015-2022 x64"

**For 32-bit Windows:**
- Download from: https://aka.ms/vs/17/release/vc_redist.x86.exe

Install the redistributable and restart the application.

### Solution 2: Bundled Application Fix

The `WindowPowerShellProvider.spec` file has been updated to better collect and bundle all OpenCV DLLs. However, Visual C++ runtime DLLs cannot be legally bundled with the application due to Microsoft's licensing restrictions.

**To rebuild the application with improved DLL collection:**
1. Rebuild using PyInstaller with the updated `.spec` file
2. The updated spec file will better capture OpenCV DLLs

### Solution 3: Automatic Fallback (Already Implemented)

The code has been updated to:
- Detect when cv2 cannot be imported
- Provide a clear error message
- Fall back to PIL-only image processing (reduced functionality but still works)

## Technical Details

OpenCV requires these Visual C++ runtime DLLs:
- `MSVCP140.dll`
- `VCRUNTIME140.dll`
- `VCRUNTIME140_1.dll`
- `api-ms-win-crt-*.dll` (various API sets)

These are provided by the Visual C++ Redistributable package.

## Verification

After installing the redistributables, verify by:
1. Running the application
2. Checking that screenshots work properly
3. No import errors should appear

## For IT/Deployment

If deploying to multiple computers:
- Include Visual C++ Redistributable installation in your deployment script
- Or ensure it's installed via group policy or software distribution
- The redistributable is a one-time install per system and doesn't conflict with other software

