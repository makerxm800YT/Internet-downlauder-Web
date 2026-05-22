#!/usr/bin/env python3
"""
Internet Download — Streamlined Media Engine Backend
Focused strictly on Video and Audio/Music downloads.
"""
import subprocess
import sys
import os

# Auto-verify or install missing core dependencies quietly
for package_name, import_name in [("flask", "flask"), ("yt-dlp", "yt_dlp"), ("static-ffmpeg", "static_ffmpeg")]:
    try:
        __import__(import_name)
    except Exception:
        print(f"Installing {package_name} dependencies safely...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "-q"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import re
import time
import uuid
import socket
import shutil
import threading
import webbrowser
from flask import Flask, request, jsonify, Response, send_from_directory
import yt_dlp
import static_ffmpeg

# Set up FFMPEG environment binaries
static_ffmpeg.add_paths()
FFMPEG_EXE = shutil.which("ffmpeg") or ""

# App working directory mappings for tracking active queues
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
    mode = payload.get("mode", "Video")  # Expected values: "Video" or "Audio Only"
    quality_tier = payload.get("quality", "Best Available")
    
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

        # Universal fallback options supporting global video & audio platforms
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

        # Apply specific format extraction filters (Video vs Audio Only)
        if "Audio" in mode:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320"
            }]
        else:
            # Map quality constraints dynamically
            if "1080p" in quality_tier:
                ydl_opts["format"] = "bestvideo[height<=1080]+bestaudio/best"
            elif "720p" in quality_tier:
                ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best"
            else:
                ydl_opts["format"] = "bestvideo+bestaudio/best"
                
            ydl_opts["merge_output_format"] = "mp4"

        try:
            # Step 1: Secure metadata info without dropping packet data
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as extractor:
                try:
                    info_dict = extractor.extract_info(url, download=False)
                    if info_dict:
                        job["title"] = info_dict.get("title", url)[:80]
                except Exception:
                    job["title"] = url[:80]

            # Step 2: Fire main download pipelines
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
        job["log"].append({"t": "Converting and processing target formats...", "c": "dim"})

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
            
            yield f"data:{jsonify_job_status(job, new_logs)}\n\n"
            if job["done"]:
                break
            time.sleep(0.3)
            
    return Response(event_generator(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

def jsonify_job_status(job, logs):
    import json
    return json.dumps({
        "status": job["status"],
        "progress": job["progress"],
        "speed": job["speed"],
        "eta": job["eta"],
        "title": job["title"],
        "logs": logs,
        "done": job["done"],
        "error": job["error"]
    })

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
    print("  INTERNET DOWNLOAD — ENGINE SERVER ACTIVE")
    print("━" * 60)
    print(f"  ▸ Local Server:   http://localhost:5000")
    print(f"  ▸ Network Access: http://{local_ip}:5000")
    print("━" * 60)
    print("  Keep this console window open to process downloads.\n")
    
    # Delayed browser auto-open 
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
