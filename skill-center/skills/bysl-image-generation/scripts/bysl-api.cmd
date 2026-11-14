@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
node "%SCRIPT_DIR%bysl-api.js" %*
exit /b %ERRORLEVEL%
