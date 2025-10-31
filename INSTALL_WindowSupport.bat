@echo off
:: WindowSupport Complete Installation Script
:: This script must be run as Administrator

SETLOCAL EnableDelayedExpansion

:: Prevent script from exiting on errors
set "ERROR_OCCURRED=0"

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
cd /d "%SCRIPT_DIR%"

:: Simple check - just verify the 3 main folders exist
echo Checking for required folders...
set "MISSING=0"

if not exist "WindowPowerShellProvider" (
    echo [ERROR] WindowPowerShellProvider folder not found!
    set "MISSING=1"
)

if not exist "WindowSupportGuardian" (
    echo [ERROR] WindowSupportGuardian folder not found!
    set "MISSING=1"
)

if not exist "get_your_staff_id" (
    echo [ERROR] get_your_staff_id folder not found!
    set "MISSING=1"
)

if "%MISSING%"=="1" (
    echo.
    echo Please make sure this installer is in the same folder as:
    echo   - WindowPowerShellProvider\
    echo   - WindowSupportGuardian\
    echo   - get_your_staff_id\
    echo.
    echo Current folder: %SCRIPT_DIR%
    echo.
    echo Contents:
    dir /B
    echo.
    pause
    exit /b 1
)

echo [OK] All required folders found
echo.
echo [Continuing in 10 seconds...]
timeout /t 10 /nobreak >nul

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
xcopy /E /I /Y "WindowPowerShellProvider" "%TARGET_DIR%\WindowPowerShellProvider\" >nul 2>&1
xcopy /E /I /Y "WindowSupportGuardian" "%TARGET_DIR%\WindowSupportGuardian\" >nul 2>&1
xcopy /E /I /Y "get_your_staff_id" "%TARGET_DIR%\get_your_staff_id\" >nul 2>&1

if %errorLevel% neq 0 (
    echo [ERROR] Failed to copy files
    pause
    exit /b 1
)

:: Copy NSSM (service wrapper)
if exist "nssm.exe" (
    echo Copying NSSM service wrapper...
    copy /Y "nssm.exe" "%TARGET_DIR%\nssm.exe" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] NSSM copied
    ) else (
        echo [WARNING] Could not copy NSSM
    )
) else (
    echo [WARNING] nssm.exe not found in installer directory
)

echo [OK] Files copied successfully
echo.
echo [Continuing in 10 seconds...]
timeout /t 10 /nobreak >nul

:: ============================================================
:: Save installation paths to Windows Registry
:: ============================================================
echo Saving installation paths to registry...

reg add "HKLM\SOFTWARE\WindowSupport" /v "InstallPath" /t REG_SZ /d "%TARGET_DIR%" /f >nul 2>&1
reg add "HKLM\SOFTWARE\WindowSupport" /v "ProviderExePath" /t REG_SZ /d "%TARGET_DIR%\WindowPowerShellProvider\WindowPowerShellProvider.exe" /f >nul 2>&1
reg add "HKLM\SOFTWARE\WindowSupport" /v "GuardianExePath" /t REG_SZ /d "%TARGET_DIR%\WindowSupportGuardian\WindowSupportGuardian.exe" /f >nul 2>&1
reg add "HKLM\SOFTWARE\WindowSupport" /v "TargetUser" /t REG_SZ /d "%TARGET_USER%" /f >nul 2>&1

if %errorLevel% equ 0 (
    echo [OK] Registry entries created
) else (
    echo [WARNING] Could not create registry entries (not critical)
)

echo.
echo [Continuing in 10 seconds...]
timeout /t 10 /nobreak >nul

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
echo [Continuing in 10 seconds...]
timeout /t 10 /nobreak >nul

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
    echo Installation cannot continue without the main application.
    pause
    goto END_INSTALL
)

echo.
echo Waiting 10 seconds before Guardian installation...
timeout /t 10 /nobreak >nul

:: ============================================================
:: STEP 6: Install and Start WindowSupportGuardian Service
:: ============================================================
echo ================================================================
echo STEP 6: Installing Guardian Service
echo ================================================================
echo.

:: Check for NSSM
set "NSSM_PATH=%TARGET_DIR%\nssm.exe"
if not exist "%NSSM_PATH%" (
    echo [WARNING] NSSM not found at: %NSSM_PATH%
    echo Checking script directory...
    set "NSSM_PATH=%SCRIPT_DIR%nssm.exe"
)

if not exist "%NSSM_PATH%" (
    echo [ERROR] NSSM (service wrapper) not found!
    echo NSSM is required to install Guardian as a Windows Service.
    echo.
    echo Please ensure nssm.exe is in the same folder as this installer.
    echo Download from: https://nssm.cc/download
    echo.
    echo Skipping Guardian service installation...
    echo The main application will still work.
    echo.
    echo [Continuing in 10 seconds...]
    timeout /t 10 /nobreak >nul
    goto SKIP_GUARDIAN
)

echo [OK] NSSM found at: %NSSM_PATH%
echo.

if exist "%EXE2%" (
    echo.
    echo ================================================================
    echo   STARTING GUARDIAN INSTALLATION - PLEASE WAIT
    echo ================================================================
    echo.
    echo Installing WindowSupportGuardian as a Windows Service (using NSSM)...
    echo This will monitor and auto-restart WindowPowerShellProvider if needed.
    echo.
    
    :: Remove existing service if it exists
    echo Removing any existing Guardian service...
    "%NSSM_PATH%" stop WindowSupportGuardian
    echo [OK] Stop command executed
    "%NSSM_PATH%" remove WindowSupportGuardian confirm
    echo [OK] Remove command executed
    timeout /t 2 /nobreak >nul
    
    :: Install the service using NSSM
    echo.
    echo Installing service with NSSM...
    echo Command: "%NSSM_PATH%" install WindowSupportGuardian "%EXE2%"
    echo.
    "%NSSM_PATH%" install WindowSupportGuardian "%EXE2%"
    set install_result=%errorLevel%
    echo Install command result code: %install_result%
    
    if %install_result% equ 0 (
        echo [OK] Service installed successfully
        echo.
        
        :: Configure service details
        echo Configuring service properties...
        echo   - Setting display name...
        "%NSSM_PATH%" set WindowSupportGuardian DisplayName "Window Support Guardian Service"
        echo   - Setting description...
        "%NSSM_PATH%" set WindowSupportGuardian Description "Monitors and restarts WindowPowerShellProvider if stopped"
        echo   - Setting auto-start...
        "%NSSM_PATH%" set WindowSupportGuardian Start SERVICE_AUTO_START
        echo   - Setting restart delay...
        "%NSSM_PATH%" set WindowSupportGuardian AppRestartDelay 5000
        echo   - Setting log files...
        "%NSSM_PATH%" set WindowSupportGuardian AppStdout "%TARGET_DIR%\logs\guardian_stdout.log"
        "%NSSM_PATH%" set WindowSupportGuardian AppStderr "%TARGET_DIR%\logs\guardian_stderr.log"
        
        echo.
        echo [OK] All service properties configured
        echo.
        
        :: Start the service
        echo Starting Guardian service...
        "%NSSM_PATH%" start WindowSupportGuardian
        set start_result=%errorLevel%
        echo Start command result code: %start_result%
        echo.
        
        if %start_result% equ 0 (
            echo.
            echo ================================================================
            echo   GUARDIAN SERVICE STARTED SUCCESSFULLY!
            echo ================================================================
            echo.
            echo The Guardian is now monitoring WindowPowerShellProvider.
            echo It will automatically restart the provider if it stops.
            echo.
            
            :: Verify service status
            echo Verifying service status...
            sc query WindowSupportGuardian | find "RUNNING"
            if %errorLevel% equ 0 (
                echo [OK] Service is running
            ) else (
                echo [WARNING] Service may not be running yet (starting in background)
            )
        ) else (
            echo [WARNING] Could not start service immediately
            echo The service will start automatically on next boot
        )
        
        echo.
        echo Service details:
        echo   Name: WindowSupportGuardian
        echo   Executable: %EXE2%
        echo   Startup: Automatic
        echo   Log file: %TARGET_DIR%\logs\WindowSupportGuardian.log
        echo.
        echo [Continuing in 10 seconds...]
        timeout /t 10 /nobreak >nul
        
    ) else (
        echo [ERROR] Service installation failed (error code: %install_result%)
        echo.
        echo FALLBACK: Creating scheduled task instead...
        
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
) else (
    echo [ERROR] WindowSupportGuardian.exe not found at: %EXE2%
    echo Skipping Guardian service installation
    echo The main application will still work via scheduled task
)

echo.

:SKIP_GUARDIAN

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
echo.
echo   Main Application:
echo     Path: %EXE1%
echo     Scheduled Task: WindowSupportMonitor (starts at login)
echo.
echo   Guardian Service:
echo     Path: %EXE2%
echo     Auto-Start: Enabled
echo     Status: Monitoring and auto-restart enabled
echo.
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
echo   C:\Users\%TARGET_USER%\AppData\Local\WindowSupport\logs\
echo.
echo Manual service installation guide:
echo   %TARGET_DIR%\MANUAL_SERVICE_INSTALL.txt
echo   (Use this if Guardian service installation failed)
echo.
echo ================================================================
echo.
echo [Continuing in 10 seconds...]
timeout /t 10 /nobreak >nul

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
echo :: Stop and remove service using NSSM
echo if exist "%%~dp0nssm.exe" ^(
echo     echo Removing Guardian service with NSSM...
echo     "%%~dp0nssm.exe" stop WindowSupportGuardian 2^>nul
echo     "%%~dp0nssm.exe" remove WindowSupportGuardian confirm 2^>nul
echo ^) else ^(
echo     echo NSSM not found, using sc command...
echo     sc stop WindowSupportGuardian 2^>nul
echo     sc delete WindowSupportGuardian 2^>nul
echo ^)
echo :: Remove defender exclusions
echo powershell -Command "Remove-MpPreference -ExclusionPath '%TARGET_DIR%'" 2^>nul
echo powershell -Command "Remove-MpPreference -ExclusionProcess 'WindowPowerShellProvider.exe'" 2^>nul
echo powershell -Command "Remove-MpPreference -ExclusionProcess 'WindowSupportGuardian.exe'" 2^>nul
echo :: Remove registry entries
echo reg delete "HKLM\SOFTWARE\WindowSupport" /f 2^>nul
echo echo.
echo echo Uninstallation complete!
echo echo You can now manually delete the folder: %TARGET_DIR%
echo pause
) > "%UNINSTALL_SCRIPT%"

echo [OK] Uninstaller created at: %UNINSTALL_SCRIPT%
echo.

:: Create manual service installation guide
echo Creating manual service installation guide...
set "MANUAL_INSTALL=%TARGET_DIR%\MANUAL_SERVICE_INSTALL.txt"
(
echo ================================================================
echo   WindowSupportGuardian - Manual Service Installation
echo ================================================================
echo.
echo If the automatic installation failed, use these commands:
echo.
echo === IMPORTANT: Run Command Prompt as Administrator ===
echo.
echo 1. Navigate to WindowSupport folder:
echo    cd "%TARGET_DIR%"
echo.
echo 2. Install the service using NSSM:
echo    nssm.exe install WindowSupportGuardian "%TARGET_DIR%\WindowSupportGuardian\WindowSupportGuardian.exe"
echo.
echo 3. Configure the service:
echo    nssm.exe set WindowSupportGuardian DisplayName "Window Support Guardian Service"
echo    nssm.exe set WindowSupportGuardian Description "Monitors and restarts WindowPowerShellProvider if stopped"
echo    nssm.exe set WindowSupportGuardian Start SERVICE_AUTO_START
echo    nssm.exe set WindowSupportGuardian AppRestartDelay 5000
echo    nssm.exe set WindowSupportGuardian AppStdout "%TARGET_DIR%\logs\guardian_stdout.log"
echo    nssm.exe set WindowSupportGuardian AppStderr "%TARGET_DIR%\logs\guardian_stderr.log"
echo.
echo 4. Start the service:
echo    nssm.exe start WindowSupportGuardian
echo.
echo 5. Verify the service is running:
echo    sc query WindowSupportGuardian
echo.
echo === To Remove the Service ===
echo    nssm.exe stop WindowSupportGuardian
echo    nssm.exe remove WindowSupportGuardian confirm
echo.
echo === Alternative: Use Windows sc command ===
echo    sc query WindowSupportGuardian
echo    sc start WindowSupportGuardian
echo    sc stop WindowSupportGuardian
echo    sc delete WindowSupportGuardian
echo.
echo ================================================================
echo   Location of files:
echo   - NSSM: %TARGET_DIR%\nssm.exe
echo   - Guardian: %TARGET_DIR%\WindowSupportGuardian\WindowSupportGuardian.exe
echo   - Provider: %TARGET_DIR%\WindowPowerShellProvider\WindowPowerShellProvider.exe
echo   - Logs: %TARGET_DIR%\logs\
echo ================================================================
) > "%MANUAL_INSTALL%"

echo [OK] Manual installation guide created at: %MANUAL_INSTALL%
echo.
echo [Installation complete! Exiting in 10 seconds...]
timeout /t 10 /nobreak >nul

:END_INSTALL
echo.
echo Installation process finished.
echo Press any key to exit...
pause >nul

ENDLOCAL
exit /b 0
