@echo off
title YouTube Downloader
color 0a
echo.
echo  =========================================
echo    YouTube Downloader  —  Starting...
echo  =========================================
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found!
    echo  Download it at: https://python.org/downloads
    echo  Check "Add Python to PATH" when installing.
    echo.
    pause & exit /b
)
echo  Installing packages...
python -m pip install yt-dlp static-ffmpeg -q 2>nul
echo  Launching app...
python "%~dp0ytdownloader.py"
if errorlevel 1 ( echo. & echo  Something went wrong. & pause )
