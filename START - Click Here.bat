@echo off
title StreamVault JS - Unlimited Downloader
color 0A

echo ========================================
echo    StreamVault JS - Starting Engine
echo ========================================

:: 1. Check for Node.js
node -v >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please install it from: https://nodejs.org/
    pause
    exit
)

:: 2. Check for package.json, if not exists, create it
if not exist "package.json" (
    echo [1/3] Initializing Project...
    call npm init -y >nul
)

:: 3. Install Dependencies (The "Unlimited" Engine)
echo [2/3] Installing Dependencies (Express + YTDL)...
call npm install express @distube/ytdl-core cors --quiet

:: 4. Launch Browser and Server
echo [3/3] Launching Web Interface...
start http://localhost:3000

echo ----------------------------------------
echo SERVER IS LIVE AT http://localhost:3000
echo KEEP THIS WINDOW OPEN TO DOWNLOAD
echo ----------------------------------------
node server.js

pause
