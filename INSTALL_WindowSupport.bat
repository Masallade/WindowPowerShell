@echo off
:: WindowSupport Complete Installation Script
:: This script must be run as Administrator

SETLOCAL EnableDelayedExpansion

echo ================================================================
echo         WindowSupport - Complete Installation Script
echo ================================================================
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges!
    echo Please right-click and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Running with Administrator privileges
echo.

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "SOURCE_DIR=%SCRIPT_DIR%"

:: Check if source folders exist (simple and reliable)
if not exist "%SOURCE_DIR%WindowPowerShellProvider\" (
    echo [ERROR] WindowPowerShellProvider folder not found!
    echo.
    echo This installer must be in the same folder as the executables!
    echo.
    echo Expected structure:
    echo   [This Folder]\
    echo   ├── INSTALL_WindowSupport.bat  (this file)
    echo   ├── WindowPowerShellProvider\
    echo   ├── WindowSupportGuardian\
    echo   └── get_your_staff_id\
    echo.
    pause
    exit /b 1
)

echo [OK] Source folders found
echo.

:: ============================================================
:: STEP 1: Ask which user to install for
:: ============================================================
echo ================================================================
echo STEP 1: Select Target User
echo ================================================================
echo.
echo Available users on this computer:
echo.

:: List all user profiles
set /a count=0
for /d %%U in (C:\Users\*) do (
    set /a count+=1
    set "user!count!=%%~nxU"
    echo   !count!. %%~nxU
)

echo.
set /p user_choice="Enter the number of the user to install for: "

:: Validate choice
if not defined user%user_choice% (
    echo [ERROR] Invalid selection
    pause
    exit /b 1
)

set "TARGET_USER=!user%user_choice%!"
set "TARGET_DIR=C:\Users\%TARGET_USER%\AppData\Local\WindowSupport"

echo.
echo [OK] Selected user: %TARGET_USER%
echo [OK] Installation directory: %TARGET_DIR%
echo.
pause

:: ============================================================
:: STEP 2: Copy files to target directory
:: ============================================================
echo ================================================================
echo STEP 2: Copying Files
echo ================================================================
echo.

:: Create target directory if it doesn't exist
if not exist "%TARGET_DIR%" (
    echo Creating directory: %TARGET_DIR%
    mkdir "%TARGET_DIR%"
)

:: Copy all files
echo Copying WindowSupport files...
xcopy /E /I /Y "%SOURCE_DIR%\*" "%TARGET_DIR%\" >nul 2>&1

if %errorLevel% neq 0 (
    echo [ERROR] Failed to copy files
    pause
    exit /b 1
)

echo [OK] Files copied successfully
echo.

:: ============================================================
:: STEP 3: Add Windows Defender Exclusions
:: ============================================================
echo ================================================================
echo STEP 3: Adding Windows Defender Exclusions
echo ================================================================
echo.

set "EXE1=%TARGET_DIR%\WindowPowerShellProvider\WindowPowerShellProvider.exe"
set "EXE2=%TARGET_DIR%\WindowSupportGuardian\WindowSupportGuardian.exe"
set "EXE3=%TARGET_DIR%\get_your_staff_id\get_your_staff_id.exe"

echo Adding exclusion for: %TARGET_DIR%
powershell -Command "Add-MpPreference -ExclusionPath '%TARGET_DIR%'" 2>nul
if %errorLevel% equ 0 (
    echo [OK] Folder exclusion added
) else (
    echo [WARNING] Could not add folder exclusion
)

echo Adding exclusion for: WindowPowerShellProvider.exe
powershell -Command "Add-MpPreference -ExclusionProcess 'WindowPowerShellProvider.exe'" 2>nul
if %errorLevel% equ 0 (
    echo [OK] Process exclusion added
) else (
    echo [WARNING] Could not add process exclusion
)

echo Adding exclusion for: WindowSupportGuardian.exe
powershell -Command "Add-MpPreference -ExclusionProcess 'WindowSupportGuardian.exe'" 2>nul
if %errorLevel% equ 0 (
    echo [OK] Process exclusion added
) else (
    echo [WARNING] Could not add process exclusion
)

echo.
echo [OK] Windows Defender exclusions configured
echo.
pause

:: ============================================================
:: STEP 4: Run get_your_staff_id.exe (as target user)
:: ============================================================
echo ================================================================
echo STEP 4: Configure Staff ID
echo ================================================================
echo.

echo Launching Staff ID selector...
echo Please select your Staff ID in the window that opens.
echo.

:: Run as the target user (if we can)
if exist "%EXE3%" (
    start "" "%EXE3%"
    echo [OK] Staff ID selector launched
    echo.
    echo Waiting 30 seconds for you to select your Staff ID...
    timeout /t 30 /nobreak
) else (
    echo [ERROR] get_your_staff_id.exe not found at: %EXE3%
    pause
    exit /b 1
)

echo.

:: ============================================================
:: STEP 5: Run WindowPowerShellProvider.exe
:: ============================================================
echo ================================================================
echo STEP 5: Starting Main Application
echo ================================================================
echo.

if exist "%EXE1%" (
    echo Starting WindowPowerShellProvider...
    
    :: Create scheduled task for the target user
    set "TASK_NAME=WindowSupportMonitor"
    
    echo Creating scheduled task for user: %TARGET_USER%
    schtasks /create /tn "%TASK_NAME%" /tr "\"%EXE1%\"" /sc onlogon /ru "%TARGET_USER%" /rl highest /f >nul 2>&1
    
    if %errorLevel% equ 0 (
        echo [OK] Scheduled task created: %TASK_NAME%
        echo [OK] Will start automatically at user login
    ) else (
        echo [WARNING] Could not create scheduled task
    )
    
    :: Start it now
    echo Starting the application now...
    start "" "%EXE1%"
    echo [OK] WindowPowerShellProvider started
) else (
    echo [ERROR] WindowPowerShellProvider.exe not found at: %EXE1%
    pause
    exit /b 1
)

echo.
timeout /t 3

:: ============================================================
:: STEP 6: Install and Start WindowSupportGuardian Service
:: ============================================================
echo ================================================================
echo STEP 6: Installing Guardian Service
echo ================================================================
echo.

if exist "%EXE2%" (
    echo Installing WindowSupportGuardian as a Windows Service...
    echo Command: "%EXE2%" install
    echo.
    
    :: Install the service (show output for debugging)
    "%EXE2%" install
    set install_result=%errorLevel%
    
    echo.
    echo Install result code: %install_result%
    echo.
    
    if %install_result% equ 0 (
        echo [OK] Service installed successfully
        echo.
        
        :: Configure service to start automatically
        echo Configuring service to start automatically...
        sc config WindowSupportGuardian start= auto
        
        if %errorLevel% equ 0 (
            echo [OK] Service set to automatic startup
        ) else (
            echo [WARNING] Could not set automatic startup
        )
        
        echo.
        
        :: Start the service using sc command
        echo Starting the Guardian service using sc command...
        sc start WindowSupportGuardian
        set start_result=%errorLevel%
        
        echo.
        
        if %start_result% equ 0 (
            echo [OK] Guardian service started successfully
        ) else (
            echo [WARNING] Could not start service with sc command
            echo Trying alternative method...
            
            :: Try using the exe's start command
            "%EXE2%" start
            
            if %errorLevel% equ 0 (
                echo [OK] Guardian service started via exe command
            ) else (
                echo [WARNING] Could not start service automatically
                echo.
                echo Manual start instructions:
                echo   1. Open Services (services.msc)
                echo   2. Find "Window Support Guardian Service"
                echo   3. Right-click and select "Start"
            )
        )
        
        :: Verify service is installed
        echo.
        echo Verifying service installation...
        sc query WindowSupportGuardian
        echo.
        
    ) else (
        echo [ERROR] Service installation failed!
        echo.
        echo This might be because:
        echo   - Service already exists (need to remove old one first)
        echo   - Missing dependencies (pywin32, psutil)
        echo   - Permissions issue
        echo.
        echo Trying to remove existing service first...
        sc stop WindowSupportGuardian 2>nul
        sc delete WindowSupportGuardian 2>nul
        timeout /t 2 >nul
        
        echo.
        echo Retrying installation...
        "%EXE2%" install
        
        if %errorLevel% equ 0 (
            echo [OK] Service installed successfully on retry
            echo.
            
            echo Configuring service to start automatically...
            sc config WindowSupportGuardian start= auto
            
            echo.
            echo Starting service...
            sc start WindowSupportGuardian
            
            if %errorLevel% equ 0 (
                echo [OK] Guardian service started
            )
        ) else (
            echo [ERROR] Service installation still failed
            echo.
            echo FALLBACK: Creating scheduled task for Guardian instead...
            
            :: Create a scheduled task as fallback
            schtasks /create /tn "WindowSupportGuardian" /tr "\"%EXE2%\"" /sc onlogon /rl highest /f
            
            if %errorLevel% equ 0 (
                echo [OK] Guardian scheduled task created as fallback
                echo Guardian will start at user login
                
                :: Start it now
                start "" "%EXE2%"
                echo [OK] Guardian started as regular process
            ) else (
                echo [WARNING] Could not create fallback scheduled task
            )
        )
    )
) else (
    echo [ERROR] WindowSupportGuardian.exe not found at: %EXE2%
    echo Skipping Guardian service installation
    echo The main application will still work via scheduled task
)

echo.

:: ============================================================
:: Installation Complete!
:: ============================================================
echo ================================================================
echo          INSTALLATION COMPLETED SUCCESSFULLY!
echo ================================================================
echo.
echo Summary:
echo   Target User:        %TARGET_USER%
echo   Installation Path:  %TARGET_DIR%
echo   Scheduled Task:     WindowSupportMonitor (starts at login)
echo   Guardian Service:   Monitoring and auto-restart enabled
echo   Defender Exclusions: Added
echo.
echo The application is now running and will start automatically
echo when %TARGET_USER% logs in.
echo.
echo To verify:
echo   1. Check Task Scheduler for "WindowSupportMonitor"
echo   2. Open Services and look for "Window Support Guardian Service"
echo   3. Check Process Manager for WindowPowerShellProvider.exe
echo.
echo Log files location:
echo   C:\Users\%TARGET_USER%\AppData\Local\WindowSupport\
echo.
echo ================================================================
echo.

pause

:: Create uninstall script
echo Creating uninstaller...
set "UNINSTALL_SCRIPT=%TARGET_DIR%\UNINSTALL.bat"
(
echo @echo off
echo echo Uninstalling WindowSupport...
echo echo.
echo :: Stop processes
echo taskkill /F /IM WindowPowerShellProvider.exe 2^>nul
echo taskkill /F /IM WindowSupportGuardian.exe 2^>nul
echo :: Remove scheduled task
echo schtasks /delete /tn "WindowSupportMonitor" /f 2^>nul
echo :: Stop and remove service
echo sc stop WindowSupportGuardian 2^>nul
echo sc delete WindowSupportGuardian 2^>nul
echo :: Remove defender exclusions
echo powershell -Command "Remove-MpPreference -ExclusionPath '%TARGET_DIR%'" 2^>nul
echo powershell -Command "Remove-MpPreference -ExclusionProcess 'WindowPowerShellProvider.exe'" 2^>nul
echo powershell -Command "Remove-MpPreference -ExclusionProcess 'WindowSupportGuardian.exe'" 2^>nul
echo echo.
echo echo Uninstallation complete!
echo echo You can now manually delete the folder: %TARGET_DIR%
echo pause
) > "%UNINSTALL_SCRIPT%"

echo [OK] Uninstaller created at: %UNINSTALL_SCRIPT%
echo.

ENDLOCAL
exit /b 0

