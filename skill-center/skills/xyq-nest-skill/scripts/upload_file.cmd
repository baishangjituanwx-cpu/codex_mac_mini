@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0upload_file.ps1" %*
exit /b %ERRORLEVEL%
