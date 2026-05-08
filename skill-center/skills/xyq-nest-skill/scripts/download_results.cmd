@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0download_results.ps1" %*
exit /b %ERRORLEVEL%
