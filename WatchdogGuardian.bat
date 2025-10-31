@echo off
setlocal EnableDelayedExpansion

rem --- config ---
set "LOGDIR=%LOCALAPPDATA%\WindowSupport\logs"
set "LOGFILE=%LOGDIR%\WatchdogGuardian.log"
set "REGKEY=HKLM\SOFTWARE\WindowSupport"
set "REGVAL=ProviderExePath"
set "CHECK_SECS=30"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

call :ts && echo [%TS%] Guardian watchdog started>>"%LOGFILE%"

:loop
  rem 1) resolve provider path (prefer registry)
  for /f "tokens=2,*" %%A in ('reg query "%REGKEY%" /v "%REGVAL%" 2^>nul ^| find /i "%REGVAL%"') do set "EXE=%%B"
  if not defined EXE if exist "%~dp0WindowPowerShellProvider\WindowPowerShellProvider.exe" set "EXE=%~dp0WindowPowerShellProvider\WindowPowerShellProvider.exe"

  rem 2) if provider not found, log and wait
  if not defined EXE (
    call :ts && echo [%TS%] Provider exe not found. Waiting...>>"%LOGFILE%"
    timeout /t %CHECK_SECS% /nobreak >nul
    goto loop
  )

  rem 3) check running
  tasklist /FI "IMAGENAME eq WindowPowerShellProvider.exe" | find /I "WindowPowerShellProvider.exe" >nul
  if errorlevel 1 (
    call :ts && echo [%TS%] Provider not running. Starting: "%EXE%">>"%LOGFILE%"
    start "" "%EXE%"
    timeout /t 5 /nobreak >nul
  )

  timeout /t %CHECK_SECS% /nobreak >nul
  goto loop

:ts
  for /f "tokens=1-3 delims=/- " %%a in ('date /t') do set "D=%%a %%b %%c"
  for /f "tokens=1-2 delims=." %%h in ('time /t') do set "T=%%h:%%i"
  set "TS=%D% %T%"
  exit /b