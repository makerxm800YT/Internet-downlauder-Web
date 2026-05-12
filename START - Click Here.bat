@echo off
title StreamVault JS - 4K Engine
color 0B

echo ========================================
echo    StreamVault JS - Fixing Engine...
echo ========================================

:: Check for Node
node -v >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js missing!
    pause
    exit
)

:: Auto-Download the yt-dlp tool if missing
if not exist "yt-dlp.exe" (
    echo [1/3] Downloading High-Speed Engine...
    powershell -Command "Invoke-WebRequest https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -OutFile yt-dlp.exe"
)

echo [2/3] Updating JS Libraries...
call npm init -y >nul
call npm install express cors --quiet

echo [3/3] Launching Web UI...
start http://localhost:3000

echo ----------------------------------------
echo SERVER LIVE - NO MORE FORMAT ERRORS
echo ----------------------------------------
node server.js
pause
