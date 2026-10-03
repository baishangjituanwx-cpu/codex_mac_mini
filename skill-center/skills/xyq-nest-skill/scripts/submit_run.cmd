@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0submit_run.ps1" %*
exit /b %ERRORLEVEL%
