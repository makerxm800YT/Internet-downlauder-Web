@echo off
title YouTube Downloader — Starting
color 0a
echo.
echo  ==========================================
echo    YouTube Downloader  v3  (Web App)
echo  ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found!
    echo  Download at: https://python.org/downloads
    echo  Check "Add Python to PATH" when installing.
    echo.
    pause & exit /b
)

echo  [1/3] Installing packages (first time may take a moment)...
python -m pip install flask yt-dlp static-ffmpeg -q 2>nul
python -m pip install flask yt-dlp static-ffmpeg -q --break-system-packages 2>nul
echo  [2/3] Packages ready.
echo  [3/3] Starting server and opening browser...
echo.
echo  The app will open in your browser automatically.
echo  Keep this window open while using the app.
echo  Close this window to shut down the app.
echo.

python "%~dp0app.py"

if errorlevel 1 (
    echo.
    echo  [ERROR] Something went wrong.
    echo  Make sure app.py and index.html are in the same folder as this file.
    pause
)
