# Simple MSI Builder
$ErrorActionPreference = 'Stop'

Write-Host "Building Window Support MSI..." -ForegroundColor Cyan

# Paths
$wixPath = "$env:WIX\bin"
$wxs = "WindowSupport.wxs"
$wixobj = "WindowSupport.wixobj"
$msi = "WindowSupport.msi"

# Check WiX
if (-not (Test-Path $wixPath)) {
    Write-Host "ERROR: WiX not found. Install from https://github.com/wixtoolset/wix3/releases" -ForegroundColor Red
    exit 1
}

# Check EXE files
$exes = @("WindowPowerShellProvider.exe", "WindowSupportGuardian.exe", "get_your_staff_id.exe")
foreach ($exe in $exes) {
    if (-not (Test-Path "..\dist\$exe")) {
        Write-Host "ERROR: $exe not found in dist folder" -ForegroundColor Red
        exit 1
    }
}

# Clean
Remove-Item $wixobj -ErrorAction SilentlyContinue
Remove-Item $msi -ErrorAction SilentlyContinue

# Compile
Write-Host "Compiling..." -ForegroundColor Green
& "$wixPath\candle.exe" -nologo -ext WixUIExtension $wxs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Link
Write-Host "Linking..." -ForegroundColor Green
& "$wixPath\light.exe" -nologo -ext WixUIExtension -out $msi $wixobj -sval
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "SUCCESS! MSI created: $msi" -ForegroundColor Green
Write-Host ""




