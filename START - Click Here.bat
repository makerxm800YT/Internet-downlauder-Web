@echo off
title YT Downloader - Starting...

echo ========================================
echo    YouTube Downloader - Starting
echo ========================================

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python from: https://python.org/downloads
    echo Make sure to check "Add Python to PATH"
    pause
    exit
)

echo [1/3] Installing / Updating packages...
python -m pip install flask yt-dlp static-ffmpeg --upgrade -q

echo [2/3] Starting Server...
echo The browser will open automatically...

:: Open browser first
start http://localhost:5000

:: Start the Python app
python app.py

pause
