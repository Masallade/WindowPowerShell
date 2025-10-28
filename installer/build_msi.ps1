# Build MSI Installer for Window Support
# Requires WiX Toolset v3.11 or later

param(
    [string]$WixPath = "$env:WIX\bin"
)

$ErrorActionPreference = 'Stop'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Window Support MSI Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if WiX is installed
if (-not (Test-Path $WixPath)) {
    Write-Host "ERROR: WiX Toolset not found at: $WixPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install WiX Toolset from:" -ForegroundColor Yellow
    Write-Host "https://github.com/wixtoolset/wix3/releases" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or set WixPath parameter:" -ForegroundColor Yellow
    Write-Host '.\build_msi.ps1 -WixPath "C:\Path\To\WiX\bin"' -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/5] Checking prerequisites..." -ForegroundColor Green

# Check if EXE files exist
$distPath = Join-Path (Split-Path $PSScriptRoot) "dist"
$exeFiles = @(
    "WindowPowerShellProvider.exe",
    "WindowSupportGuardian.exe",
    "get_your_staff_id.exe"
)

foreach ($exe in $exeFiles) {
    $exePath = Join-Path $distPath $exe
    if (-not (Test-Path $exePath)) {
        Write-Host "ERROR: $exe not found in dist\ folder" -ForegroundColor Red
        Write-Host "Please build EXE files first using PyInstaller" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "  ✓ Found: $exe" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[2/5] Cleaning old build files..." -ForegroundColor Green

# Clean old build files
$wxs = Join-Path $PSScriptRoot 'WindowSupport.wxs'
$wixobj = Join-Path $PSScriptRoot 'WindowSupport.wixobj'
$wixpdb = Join-Path $PSScriptRoot 'WindowSupport.wixpdb'
$msi = Join-Path $PSScriptRoot 'WindowSupport.msi'

if (Test-Path $wixobj) { Remove-Item $wixobj -Force }
if (Test-Path $wixpdb) { Remove-Item $wixpdb -Force }
if (Test-Path $msi) { Remove-Item $msi -Force }

Write-Host "  ✓ Cleaned" -ForegroundColor Gray
Write-Host ""

Write-Host "[3/5] Compiling WiX source..." -ForegroundColor Green

# Compile WiX source
$candleArgs = @(
    "-nologo",
    "-ext", "WixUIExtension",
    "-out", $wixobj,
    $wxs
)

& "$WixPath\candle.exe" @candleArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Compilation failed" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "  ✓ Compiled successfully" -ForegroundColor Gray
Write-Host ""

Write-Host "[4/5] Linking MSI package..." -ForegroundColor Green

# Link MSI
$lightArgs = @(
    "-nologo",
    "-ext", "WixUIExtension",
    "-out", $msi,
    $wixobj,
    "-sval"  # Suppress validation warnings
)

& "$WixPath\light.exe" @lightArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Linking failed" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "  ✓ Linked successfully" -ForegroundColor Gray
Write-Host ""

Write-Host "[5/5] Finalizing..." -ForegroundColor Green

# Get MSI info
$msiSize = (Get-Item $msi).Length / 1MB
Write-Host "  ✓ MSI Size: $([math]::Round($msiSize, 2)) MB" -ForegroundColor Gray

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SUCCESS! MSI created:" -ForegroundColor Green
Write-Host $msi -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now install with:" -ForegroundColor Yellow
Write-Host "  msiexec /i WindowSupport.msi" -ForegroundColor White
Write-Host ""
Write-Host 'Or double-click the MSI file to install.' -ForegroundColor Yellow
Write-Host ""
