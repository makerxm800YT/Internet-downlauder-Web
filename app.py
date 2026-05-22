#!/usr/bin/env python3
"""
Internet Download — Multi-Format Media Engine Backend
Supports all common video formats (mp4, mkv, webm, avi, flv, mov) 
and audio/music formats (mp3, m4a, flac, wav, opus, aac) across all qualities.
"""
import subprocess
import sys
import os

# Auto-verify or install missing core dependencies quietly
for package_name, import_name in [("flask", "flask"), ("yt-dlp", "yt_dlp"), ("static-ffmpeg", "static_ffmpeg")]:
    try:
        __import__(import_name)
    except Exception:
        print(f"Installing missing dependency: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "-q"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import re
import time
import uuid
import json
import socket
import shutil
import threading
import webbrowser
from flask import Flask, request, jsonify, Response, send_from_directory
import yt_dlp
import static_ffmpeg

# Bind FFMPEG environment binaries for conversions
static_ffmpeg.add_paths()
FFMPEG_EXE = shutil.which("ffmpeg") or ""

APP_DIR = os.path.join(os.path.expanduser("~"), ".internet_download_app")
os.makedirs(APP_DIR, exist_ok=True)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, template_folder=SCRIPT_DIR)
_active_jobs = {}

def get_local_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

@app.route("/")
def index():
    return send_from_directory(SCRIPT_DIR, "index.html")

@app.route("/favicon.svg")
def favicon():
    return send_from_directory(SCRIPT_DIR, "favicon.svg")

@app.route("/api/download", methods=["POST"])
def start_media_download():
    payload = request.json or {}
    url = payload.get("url", "").strip()
    mode = payload.get("mode", "Video")            # "Video" or "Audio Only"
    quality_tier = payload.get("quality", "Best Available") # "Best Available", "4K", "1080p", "720p", "480p", "360p"
    target_format = payload.get("format", "mp4").lower().strip() # mp4, mkv, mp3, flac, etc.
    
    if not url:
        return jsonify(error="A valid URL resource link is required."), 400

    job_id = str(uuid.uuid4())[:8]
    _active_jobs[job_id] = {
        "status": "starting",
        "progress": 0,
        "speed": "",
        "eta": "",
        "log": [],
        "title": "Extracting stream details...",
        "done": False,
        "error": None
    }

    def download_worker_thread():
        job = _active_jobs[job_id]
        download_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(download_directory, exist_ok=True)

        # Base configuration template
        ydl_opts = {
            "outtmpl": os.path.join(download_directory, "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True,
            "progress_hooks": [lambda data: progress_hook_callback(job, data)],
        }

        if FFMPEG_EXE:
            ydl_opts["ffmpeg_location"] = os.path.dirname(FFMPEG_EXE)

        # Catch specific metadata or music tracking setups automatically
        if "spotify.com" in url.lower():
            ydl_opts["default_search"] = "ytsearch"
            nonlocal mode
            mode = "Audio Only"

        # --- DYNAMIC FORMAT & QUALITY SELECTION ENGINE ---
        if "audio" in mode.lower() or target_format in ["mp3", "m4a", "flac", "wav", "opus", "aac"]:
            # Setup pure music extraction rules
            ydl_opts["format"] = "bestaudio/best"
            
            # Normalize target music formats
            valid_audio = ["mp3", "m4a", "flac", "wav", "opus", "aac"]
            audio_codec = target_format if target_format in valid_audio else "mp3"
            
            # Use maximum bitrate rules or native lossless depending on configuration choices
            audio_quality = "0" if audio_codec in ["flac", "wav"] else "320"
            
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_codec,
                "preferredquality": audio_quality
            }]
        else:
            # Setup dynamic video mapping parameters based on selection arrays
            video_resolutions = {
                "4k": "bestvideo[height<=2160]+bestaudio/best",
                "1080p": "bestvideo[height<=1080]+bestaudio/best",
                "720p": "bestvideo[height<=720]+bestaudio/best",
                "480p": "bestvideo[height<=480]+bestaudio/best",
                "360p": "bestvideo[height<=360]+bestaudio/best"
            }
            
            # Find closest quality resolution profile matching
            quality_key = next((k for k in video_resolutions if k in quality_tier.lower()), None)
            ydl_opts["format"] = video_resolutions.get(quality_key, "bestvideo+bestaudio/best")
            
            # Handle common container wrappers
            valid_video = ["mp4", "mkv", "webm", "avi", "flv", "mov"]
            video_container = target_format if target_format in valid_video else "mp4"
            ydl_opts["merge_output_format"] = video_container

        try:
            # Step 1: Attempt to read info headers safely
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as extractor:
                try:
                    info_dict = extractor.extract_info(url, download=False)
                    if info_dict:
                        job["title"] = info_dict.get("title", url)[:80]
                except Exception:
                    job["title"] = url[:80]

            # Step 2: Fire primary download execution pipelines
            job["status"] = "downloading"
            with yt_dlp.YoutubeDL(ydl_opts) as downloader:
                downloader.download([url])

            job.update({
                "status": "done",
                "progress": 100,
                "done": True
            })
            job["log"].append({"t": f"✓ File saved successfully to your Downloads directory", "c": "ok"})

        except Exception as err:
            job.update({
                "status": "error",
                "error": str(err),
                "done": True
            })
            job["log"].append({"t": f"✗ Error processing stream: {err}", "c": "err"})

    threading.Thread(target=download_worker_thread, daemon=True).start()
    return jsonify(job_id=job_id)

def progress_hook_callback(job, data):
    if data["status"] == "downloading":
        percent_str = data.get("_percent_str", "0%").strip()
        parsed_pct = float(re.sub(r"[^\d.]", "", percent_str) or 0)
        job.update({
            "progress": parsed_pct,
            "speed": data.get("_speed_str", "").strip(),
            "eta": data.get("_eta_str", "").strip()
        })
    elif data["status"] == "finished":
        job["status"] = "processing"
        job["log"].append({"t": "Converting and muxing files into destination format wrappers...", "c": "dim"})

@app.route("/api/progress/<jid>")
def tracking_progress_stream(jid):
    def event_generator():
        last_logged_index = 0
        while True:
            job = _active_jobs.get(jid)
            if not job:
                yield f"data:{json.dumps({'error': 'Job ID entry not found'})}\n\n"
                break
                
            new_logs = job["log"][last_logged_index:]
            last_logged_index = len(job["log"])
            
            yield f"data:{json.dumps({
                'status': job['status'],
                'progress': job['progress'],
                'speed': job['speed'],
                'eta': job['eta'],
                'title': job['title'],
                'logs': new_logs,
                'done': job['done'],
                'error': job['error']
            })}\n\n"
            
            if job["done"]:
                break
            time.sleep(0.3)
            
    return Response(event_generator(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.route("/api/info")
def engine_environment_info():
    return jsonify(
        ytdlp=yt_dlp.version.__version__,
        ffmpeg=bool(FFMPEG_EXE),
        network=f"http://{get_local_ip_address()}:5000"
    )

if __name__ == "__main__":
    local_ip = get_local_ip_address()
    print("\n" + "━" * 60)
    print("  INTERNET DOWNLOAD — MULTI-FORMAT ENGINE ACTIVE")
    print("━" * 60)
    print(f"  ▸ Local Server:   http://localhost:5000")
    print(f"  ▸ Network Access: http://{local_ip}:5000")
    print("━" * 60)
    print("  Processing video / music formats safely. Keep this window open.\n")
    
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
