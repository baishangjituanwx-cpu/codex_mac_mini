@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0mirror-view.ps1" %*
set "exit_code=%ERRORLEVEL%"
if not "%exit_code%"=="0" exit /b %exit_code%
echo.
pause
