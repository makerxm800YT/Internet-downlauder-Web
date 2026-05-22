#!/usr/bin/env python3
"""
YTDL — YouTube Downloader
Modern • Private • Fast
"""

import subprocess, sys, os

def pip(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Install dependencies
for p, i in [("flask", "flask"), ("yt-dlp", "yt_dlp"), ("static-ffmpeg", "static_ffmpeg")]:
    try:
        __import__(i)
    except:
        print(f"Installing {p}...")
        pip(p)

from flask import Flask, request, jsonify, Response, send_from_directory
import yt_dlp, static_ffmpeg, shutil, json, hashlib, datetime
import threading, uuid, re, time, socket, webbrowser

static_ffmpeg.add_paths()
FFMPEG = shutil.which("ffmpeg") or ""

APP_DIR = os.path.join(os.path.expanduser("~"), ".ytdl_app")
ACCS_FILE = os.path.join(APP_DIR, "accounts.json")
HIST_FILE = os.path.join(APP_DIR, "history.json")
os.makedirs(APP_DIR, exist_ok=True)

def jload(p, d):
    try:
        with open(p) as f: return json.load(f)
    except: return d

def jsave(p, d):
    with open(p, "w") as f: json.dump(d, f, indent=2)

def hashpw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: return "localhost"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, template_folder=SCRIPT_DIR)

_jobs = {}

@app.route("/")
def index():
    return send_from_directory(SCRIPT_DIR, "index.html")

@app.route("/favicon.svg")
def favicon():
    return send_from_directory(SCRIPT_DIR, "favicon.svg")

# ── Auth (kept simple but working) ─────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    d = request.json or {}
    accs = jload(ACCS_FILE, {})
    email = d.get("email","").strip().lower()
    pw = d.get("password","")
    name = d.get("name","").strip()
    
    if not email or "@" not in email: return jsonify(error="Invalid email"), 400
    if not pw or len(pw) < 6: return jsonify(error="Password too short"), 400
    if not name: return jsonify(error="Name required"), 400
    if email in accs: return jsonify(error="Account already exists"), 409

    accs[email] = {"name": name, "pw_hash": hashpw(pw), "joined": str(datetime.date.today()), "method": "email"}
    jsave(ACCS_FILE, accs)
    return jsonify(ok=True, name=name, email=email)

@app.route("/api/login", methods=["POST"])
def login():
    d = request.json or {}
    accs = jload(ACCS_FILE, {})
    email = d.get("email","").strip().lower()
    pw = d.get("password","")
    
    if email not in accs or accs[email].get("pw_hash") != hashpw(pw):
        return jsonify(error="Wrong email or password"), 401
    
    u = accs[email]
    return jsonify(ok=True, name=u["name"], email=email)

@app.route("/api/google-login", methods=["POST"])
def google_login():
    d = request.json or {}
    accs = jload(ACCS_FILE, {})
    email = d.get("email","").strip().lower()
    if not email or "@" not in email: return jsonify(error="Invalid Gmail"), 400
    
    if email not in accs:
        gname = email.split("@")[0].replace(".", " ").title()
        accs[email] = {"name": gname, "pw_hash": "", "joined": str(datetime.date.today()), "method": "google"}
        jsave(ACCS_FILE, accs)
    
    u = accs[email]
    return jsonify(ok=True, name=u["name"], email=email)

# ── Download Core ─────────────────────────────────────────────────────
@app.route("/api/download", methods=["POST"])
def start_download():
    d = request.json or {}
    url = d.get("url", "").strip()
    mode = d.get("mode", "Video")
    quality = d.get("quality", "Best (Max Quality)")

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
                'noplaylist': "Playlist" not in mode,
            }

            if "Audio" in mode:
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]
            else:
                qmap = {"Best (Max Quality)": "bestvideo+bestaudio/best", "1080p": "bestvideo[height<=1080]+bestaudio/best", "720p": "bestvideo[height<=720]+bestaudio/best"}
                opts["format"] = qmap.get(quality, "bestvideo+bestaudio/best")

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                job["title"] = info.get('title', 'Video')
                ydl.download([url])

            job["status"] = "done"
            job["progress"] = 100
            job["done"] = True
            job["log"].append("✅ Download Finished!")

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
    print("\n" + "═"*55)
    print("   🎥 YTDL — YouTube Downloader")
    print("═"*55)
    print(f"   Local   →  http://localhost:5000")
    print(f"   Network →  http://{ip}:5000")
    print("═"*55)
    
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
