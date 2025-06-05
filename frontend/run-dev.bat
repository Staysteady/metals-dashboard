@echo off
setlocal

REM Set the path to portable Node.js
set NODE_PATH=C:\Mac\Home\Documents\nodejs-portable\node-v20.18.2-win-x64
set PATH=%NODE_PATH%;%PATH%

REM Change to frontend directory
cd /d C:\Mac\Home\Documents\metals-dashboard\frontend

REM Display versions
echo Using Node.js and npm versions:
"%NODE_PATH%\node.exe" --version
"%NODE_PATH%\npm.cmd" --version

REM Run the development server
echo.
echo Starting Metals Dashboard...
"%NODE_PATH%\npm.cmd" run dev

pause 