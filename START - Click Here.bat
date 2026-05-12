@echo off
title StreamVault Desktop - Engine Setup
color 0B

echo ========================================
echo    StreamVault - Audio/Video Fix
echo ========================================

:: 1. Download yt-dlp if missing
if not exist "yt-dlp.exe" (
    echo [1/3] Downloading High-Speed Engine...
    powershell -Command "Invoke-WebRequest https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -OutFile yt-dlp.exe"
)

:: 2. DOWNLOAD FFMPEG (The Sound Fix)
if not exist "ffmpeg.exe" (
    echo [2/3] Downloading Audio Merger (FFmpeg)...
    echo This might take a minute, but it fixes the "No Sound" bug!
    powershell -Command "Invoke-WebRequest https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip -OutFile ffmpeg.zip"
    powershell -Command "Expand-Archive -Path ffmpeg.zip -DestinationPath temp_ffmpeg -Force"
    copy "temp_ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" "ffmpeg.exe"
    copy "temp_ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe" "ffprobe.exe"
    del ffmpeg.zip
    rmdir /s /q temp_ffmpeg
)

echo [3/3] Launching Stable Web Interface...
call npm install express cors --quiet
start http://localhost:3000
node server.js
pause
