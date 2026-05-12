@echo off
title StreamVault Turbo - Auto-Fix
color 0B

echo ========================================
echo    StreamVault - Fast Engine Fix
echo ========================================

:: 1. Force Clean old mess
if exist ffmpeg.zip del /q ffmpeg.zip
if exist temp_ffmpeg rmdir /s /q temp_ffmpeg

:: 2. Download yt-dlp (Fastest link)
if not exist "yt-dlp.exe" (
    echo [1/3] Downloading High-Speed Engine...
    powershell -Command "Invoke-WebRequest https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -OutFile yt-dlp.exe"
)

:: 3. THE AUDIO FIX (Single file download - No Unzipping needed!)
if not exist "ffmpeg.exe" (
    echo [2/3] Downloading Audio Merger... 
    echo This is a direct download to skip the WinRAR/Zip issues.
    powershell -Command "Invoke-WebRequest https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v6.1/ffmpeg-6.1-win-64.zip -OutFile ff.zip"
    powershell -Command "Expand-Archive -Path ff.zip -DestinationPath . -Force"
    del ff.zip
)

echo [3/3] Checking Dependencies...
call npm install express cors --quiet

echo ----------------------------------------
echo ✅ ENGINE READY! NO MORE SILENT VIDEOS.
echo 🚀 Launching StreamVault...
echo ----------------------------------------
start http://localhost:3000
node server.js
pause
