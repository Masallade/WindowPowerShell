# PowerShell script to rebuild all executables with fixed configuration
# Run this script to rebuild the executables after the fixes

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Building WindowSupport Executables" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking PyInstaller installation..." -ForegroundColor Yellow
try {
    $pyinstallerVersion = & pyinstaller --version 2>&1
    Write-Host "PyInstaller found: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "PyInstaller not found! Installing..." -ForegroundColor Red
    pip install pyinstaller
}

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "Removed build directory" -ForegroundColor Green
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "Removed dist directory" -ForegroundColor Green
}

# Build get_your_staff_id.exe
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Building get_your_staff_id.exe..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
pyinstaller get_your_staff_id.spec --clean
if ($LASTEXITCODE -eq 0) {
    Write-Host "get_your_staff_id.exe built successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to build get_your_staff_id.exe" -ForegroundColor Red
    exit 1
}

# Build WindowPowerShellProvider.exe
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Building WindowPowerShellProvider.exe..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
pyinstaller WindowPowerShellProvider.spec --clean
if ($LASTEXITCODE -eq 0) {
    Write-Host "WindowPowerShellProvider.exe built successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to build WindowPowerShellProvider.exe" -ForegroundColor Red
    exit 1
}

# Build WindowSupportGuardian.exe
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Building WindowSupportGuardian.exe..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
pyinstaller WindowSupportGuardian.spec --clean
if ($LASTEXITCODE -eq 0) {
    Write-Host "WindowSupportGuardian.exe built successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to build WindowSupportGuardian.exe" -ForegroundColor Red
    exit 1
}

# Copy to distribution directory
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Organizing distribution files..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$distDir = "dist\WindowSupport"
if (Test-Path $distDir) {
    Remove-Item -Recurse -Force $distDir
}
New-Item -ItemType Directory -Force -Path $distDir | Out-Null

# Copy each built application
Copy-Item -Recurse "dist\get_your_staff_id" -Destination "$distDir\get_your_staff_id"
Copy-Item -Recurse "dist\WindowPowerShellProvider" -Destination "$distDir\WindowPowerShellProvider"
Copy-Item -Recurse "dist\WindowSupportGuardian" -Destination "$distDir\WindowSupportGuardian"

Write-Host "All executables organized in: $distDir" -ForegroundColor Green

# Copy NSSM to the distribution directory
Write-Host ""
Write-Host "Copying NSSM (service wrapper) to distribution directory..." -ForegroundColor Yellow
if (Test-Path "nssm.exe") {
    Copy-Item "nssm.exe" -Destination "$distDir\nssm.exe"
    Write-Host "NSSM copied: nssm.exe" -ForegroundColor Green
} else {
    Write-Host "ERROR: nssm.exe not found! Please download from https://nssm.cc/download" -ForegroundColor Red
    Write-Host "Extract nssm.exe (64-bit) to the project root directory" -ForegroundColor Red
}

# Copy the installer to the distribution directory
Write-Host ""
Write-Host "Copying installer to distribution directory..." -ForegroundColor Yellow
if (Test-Path "INSTALL_WindowSupport.bat") {
    Copy-Item "INSTALL_WindowSupport.bat" -Destination "$distDir\INSTALL_WindowSupport.bat"
    Write-Host "Installer copied: INSTALL_WindowSupport.bat" -ForegroundColor Green
} else {
    Write-Host "Warning: INSTALL_WindowSupport.bat not found in current directory" -ForegroundColor Yellow
}

# Create installation instructions file instead of launcher
$installInstructions = @"
================================================================
       WindowSupport - Installation Required
================================================================

DO NOT run the executables directly from this folder!

PROPER INSTALLATION STEPS:
==========================

1. Right-click: INSTALL_WindowSupport.bat (in this folder)
2. Select: "Run as Administrator"
3. Follow the on-screen prompts

The installer will:
  - Ask which user to install for
  - Copy files to C:\Users\[USER]\AppData\Local\WindowSupport\
  - Add Windows Defender exclusions
  - Configure Staff ID
  - Create scheduled task (auto-start)
  - Install Guardian service
  - Set up everything automatically

================================================================

After installation, the application will run from:
C:\Users\[USER]\AppData\Local\WindowSupport\

The application will start automatically at login.

================================================================
"@
Set-Content -Path "$distDir\INSTALLATION_REQUIRED.txt" -Value $installInstructions

Write-Host "Created installation guide: INSTALLATION_REQUIRED.txt" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "BUILD COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Built executables are in: $distDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "RECOMMENDED - Use the installer:" -ForegroundColor Cyan
Write-Host "  Right-click: $distDir\INSTALL_WindowSupport.bat" -ForegroundColor White
Write-Host "  Select: Run as Administrator" -ForegroundColor White
Write-Host ""
Write-Host "OR test manually:" -ForegroundColor Cyan
Write-Host "  1. Run: $distDir\get_your_staff_id\get_your_staff_id.exe" -ForegroundColor White
Write-Host "  2. Select your staff ID" -ForegroundColor White
Write-Host "  3. Run: $distDir\WindowPowerShellProvider\WindowPowerShellProvider.exe" -ForegroundColor White
Write-Host "  4. Check Task Scheduler for WindowSupportMonitor task" -ForegroundColor White
Write-Host ""
Write-Host "The application will now:" -ForegroundColor Cyan
Write-Host "  - Not crash with PyInstaller errors" -ForegroundColor Green
Write-Host "  - Automatically add itself to Windows startup" -ForegroundColor Green
Write-Host "  - Show detailed debug output for troubleshooting" -ForegroundColor Green
Write-Host ""
Write-Host "DISTRIBUTION:" -ForegroundColor Yellow
Write-Host "  The entire $distDir folder is ready to distribute!" -ForegroundColor White
Write-Host "  It includes:" -ForegroundColor White
Write-Host "    - All executables (with dependencies)" -ForegroundColor Gray
Write-Host "    - nssm.exe (Windows Service wrapper)" -ForegroundColor Gray
Write-Host "    - INSTALL_WindowSupport.bat (the installer)" -ForegroundColor Gray
Write-Host "    - INSTALLATION_REQUIRED.txt (instructions)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Just copy this folder to any Windows machine and run the installer!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT:" -ForegroundColor Yellow
Write-Host "  WindowSupportGuardian now uses NSSM for Windows Service functionality" -ForegroundColor White
Write-Host "  - No pythonservice.exe required!" -ForegroundColor Green
Write-Host "  - Simpler, more reliable service installation" -ForegroundColor Green
Write-Host "  - All monitoring features preserved" -ForegroundColor Green
Write-Host ""
