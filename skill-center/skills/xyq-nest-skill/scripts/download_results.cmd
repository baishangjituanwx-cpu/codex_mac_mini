@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0download_results.ps1" %*
exit /b %ERRORLEVEL%
