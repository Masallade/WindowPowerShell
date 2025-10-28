@echo off
echo ================================================================
echo Checking WindowSupport Logs
echo ================================================================
echo.

set "LOG_PATH=C:\Users\avant\AppData\Local\WindowSupport\app.log"
set "ERROR_LOG_PATH=C:\Users\avant\AppData\Local\WindowSupport\error_logs.txt"

if exist "%LOG_PATH%" (
    echo [OK] Found application log
    echo.
    echo Last 50 lines of app.log:
    echo ----------------------------------------------------------------
    powershell -Command "Get-Content '%LOG_PATH%' -Tail 50"
    echo ----------------------------------------------------------------
) else (
    echo [INFO] No application log found yet at: %LOG_PATH%
)

echo.
echo.

if exist "%ERROR_LOG_PATH%" (
    echo [OK] Found error log
    echo.
    echo Contents of error_logs.txt:
    echo ----------------------------------------------------------------
    type "%ERROR_LOG_PATH%"
    echo ----------------------------------------------------------------
) else (
    echo [INFO] No error log found (this is good!)
)

echo.
echo.

echo Checking if WindowPowerShellProvider is currently running...
tasklist | find /i "WindowPowerShellProvider.exe" >nul 2>&1

if %errorLevel% equ 0 (
    echo [OK] WindowPowerShellProvider.exe is RUNNING
    tasklist | find /i "WindowPowerShellProvider.exe"
) else (
    echo [INFO] WindowPowerShellProvider.exe is NOT running
)

echo.
echo.

echo Checking scheduled task...
schtasks /query /tn "WindowSupportMonitor" >nul 2>&1

if %errorLevel% equ 0 (
    echo [OK] Scheduled task EXISTS
    echo.
    schtasks /query /tn "WindowSupportMonitor" /v /fo list | findstr /C:"Task To Run" /C:"Status" /C:"Run As User"
) else (
    echo [INFO] Scheduled task does NOT exist
)

echo.
pause



