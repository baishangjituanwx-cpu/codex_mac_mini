@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0get_thread.ps1" %*
exit /b %ERRORLEVEL%
