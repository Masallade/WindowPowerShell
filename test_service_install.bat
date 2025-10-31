@echo off
echo Testing Guardian Service Installation...
echo.

cd /d "C:\Users\avant\AppData\Local\WindowSupport\WindowSupportGuardian"

echo Running: WindowSupportGuardian.exe install
echo.
WindowSupportGuardian.exe install

echo.
echo Exit Code: %errorLevel%
echo.

if %errorLevel% equ 0 (
    echo [SUCCESS] Service installation command completed
    echo.
    echo Checking if service exists...
    sc query WindowSupportGuardian
) else (
    echo [ERROR] Service installation failed with code: %errorLevel%
)

echo.
pause


