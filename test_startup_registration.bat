@echo off
:: Test script to check why startup registration isn't working
echo ================================================================
echo Testing WindowSupport Startup Registration
echo ================================================================
echo.

set "EXE_PATH=C:\Users\avant\AppData\Local\WindowSupport\WindowPowerShellProvider\WindowPowerShellProvider.exe"
set "TASK_NAME=WindowSupportMonitor"

:: Check if exe exists
if not exist "%EXE_PATH%" (
    echo [ERROR] Executable not found at: %EXE_PATH%
    echo.
    echo Please update the EXE_PATH variable in this script to the correct location.
    pause
    exit /b 1
)

echo [OK] Found executable at: %EXE_PATH%
echo.

:: Check if task already exists
echo Checking if scheduled task already exists...
schtasks /query /tn "%TASK_NAME%" >nul 2>&1

if %errorLevel% equ 0 (
    echo [INFO] Task already exists!
    echo.
    echo Current task details:
    schtasks /query /tn "%TASK_NAME%" /v /fo list | findstr /C:"Task To Run" /C:"Status" /C:"Run As User"
    echo.
    echo Do you want to delete and recreate it? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo Deleting old task...
        schtasks /delete /tn "%TASK_NAME%" /f
        if %errorLevel% equ 0 (
            echo [OK] Old task deleted
        ) else (
            echo [ERROR] Failed to delete old task
            pause
            exit /b 1
        )
    ) else (
        echo Keeping existing task. Exiting...
        pause
        exit /b 0
    )
)

:: Create the scheduled task
echo.
echo Creating scheduled task...
echo Task Name: %TASK_NAME%
echo Executable: %EXE_PATH%
echo.

schtasks /create /tn "%TASK_NAME%" /tr "\"%EXE_PATH%\"" /sc onlogon /rl highest /f

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Scheduled task created successfully!
    echo.
    echo Verifying...
    schtasks /query /tn "%TASK_NAME%" /v /fo list | findstr /C:"Task To Run" /C:"Status" /C:"Run As User" /C:"Logon Mode"
    echo.
    echo ================================================================
    echo Task created successfully!
    echo.
    echo The application will now start automatically when you log in.
    echo ================================================================
) else (
    echo.
    echo [ERROR] Failed to create scheduled task!
    echo Error code: %errorLevel%
    echo.
    echo This might be because:
    echo   - You don't have Administrator privileges
    echo   - Group Policy restrictions
    echo   - Task Scheduler service is not running
    echo.
    echo Try running this script as Administrator.
)

echo.
pause



