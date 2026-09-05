@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0send_feishu_notify.ps1" %*
exit /b %ERRORLEVEL%
