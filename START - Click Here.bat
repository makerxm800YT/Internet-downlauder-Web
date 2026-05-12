@echo off
title StreamVault Pro - Auto Repair
color 0A

echo ========================================
echo    StreamVault - Steel-Stable Fix
echo ========================================

:: 1. Clean up old broken files
if exist ffmpeg.zip del /q ffmpeg.zip
if exist yt-dlp.exe del /q yt-dlp.exe

:: 2. Download yt-dlp.exe
echo [1/3] Downloading High-Speed Engine...
powershell -Command "Invoke-WebRequest https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -OutFile yt-dlp.exe"

:: 3. Download FFmpeg (THE AUDIO FIX)
echo [2/3] Downloading Audio Engine (FFmpeg)...
echo Please wait, this is a large file and it FIXES THE SOUND.
powershell -Command "Invoke-WebRequest https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip -OutFile ffmpeg.zip"

echo [3/3] Extracting Audio Engine...
powershell -Command "Expand-Archive -Path ffmpeg.zip -DestinationPath temp_ff -Force"

:: Move the specific exe files to the main folder
move /y "temp_ff\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" "ffmpeg.exe"
move /y "temp_ff\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe" "ffprobe.exe"

:: Cleanup
rd /s /q temp_ff
del /q ffmpeg.zip

echo ----------------------------------------
echo ✅ REPAIR COMPLETE: yt-dlp and ffmpeg are ready.
echo 🚀 Launching Server...
echo ----------------------------------------
call npm install express cors --quiet
start http://localhost:3000
node server.js
pause
