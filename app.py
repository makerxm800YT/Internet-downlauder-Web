#!/usr/bin/env python3
"""
Internet Downloader — Beautiful & Private
"""

import subprocess, sys, os

def pip(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for p, i in [("flask", "flask"), ("yt-dlp", "yt_dlp"), ("static-ffmpeg", "static_ffmpeg")]:
    try: __import__(i)
    except: print(f"Installing {p}..."); pip(p)

from flask import Flask, request, jsonify, Response, send_from_directory
import yt_dlp, static_ffmpeg, shutil, json, datetime
import threading, uuid, time, socket, webbrowser

static_ffmpeg.add_paths()
FFMPEG = shutil.which("ffmpeg") or ""

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, template_folder=SCRIPT_DIR)

_jobs = {}

@app.route("/")
def index():
    return send_from_directory(SCRIPT_DIR, "index.html")

@app.route("/favicon.svg")
def favicon():
    return send_from_directory(SCRIPT_DIR, "favicon.svg")

@app.route("/api/download", methods=["POST"])
def start_download():
    d = request.json or {}
    url = d.get("url", "").strip()
    if not url:
        return jsonify(error="No URL provided"), 400

    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {"status":"starting", "progress":0, "speed":"", "eta":"", "log":[], "title":"", "done":False}

    def run():
        job = _jobs[job_id]
        try:
            job["status"] = "downloading"
            job["log"].append("Starting download...")

            def hook(d):
                if d.get('status') == 'downloading':
                    p = d.get('_percent_str', '0').replace('%','').strip()
                    job["progress"] = float(p) / 100 if p.replace('.','').isdigit() else 0
                    job["speed"] = d.get('_speed_str', '')
                    job["eta"] = d.get('_eta_str', '')

            opts = {
                'outtmpl': os.path.join(os.path.expanduser("~"), "Downloads", '%(title)s.%(ext)s'),
                'progress_hooks': [hook],
                'merge_output_format': 'mp4',
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                job["title"] = info.get('title', 'Video')
                ydl.download([url])

            job["status"] = "done"
            job["progress"] = 100
            job["done"] = True
            job["log"].append("✅ Download Completed!")

        except Exception as e:
            job["status"] = "error"
            job["log"].append(f"Error: {str(e)}")
            job["done"] = True

    threading.Thread(target=run, daemon=True).start()
    return jsonify(job_id=job_id)

@app.route("/api/progress/<job_id>")
def progress(job_id):
    def stream():
        while True:
            job = _jobs.get(job_id)
            if not job: break
            yield f"data: {json.dumps(job)}\n\n"
            if job.get("done"): break
            time.sleep(0.3)
    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    ip = local_ip()
    print("\n" + "═"*65)
    print("   🌐 Internet Downloader")
    print("═"*65)
    print(f"   Local   →  http://localhost:5000")
    print(f"   Network →  http://{ip}:5000")
    print("═"*65)
    
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: return "localhost"
