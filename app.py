#!/usr/bin/env python3
"""
YouTube Downloader Web Server - FIXED & WORKING
"""

import subprocess, sys, os

def pip(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Install dependencies if missing
for p, i in [("flask", "flask"), ("yt-dlp", "yt_dlp"), ("static-ffmpeg", "static_ffmpeg")]:
    try:
        __import__(i)
    except:
        print(f"Installing {p}...")
        pip(p)

from flask import Flask, request, jsonify, Response, send_from_directory, send_file
import yt_dlp, static_ffmpeg, shutil, json, hashlib, datetime
import threading, uuid, time, socket, re

static_ffmpeg.add_paths()
FFMPEG = shutil.which("ffmpeg") or ""

APP_DIR = os.path.join(os.path.expanduser("~"), ".ytdl_app")
ACCS_FILE = os.path.join(APP_DIR, "accounts.json")
HIST_FILE = os.path.join(APP_DIR, "history.json")
DOWNLOAD_DIR = os.path.join(APP_DIR, "downloads")

os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def jload(p, d):
    try:
        with open(p) as f: return json.load(f)
    except: return d

def jsave(p, d):
    with open(p, "w") as f: json.dump(d, f, indent=2)

def hashpw(pw): 
    return hashlib.sha256(pw.encode()).hexdigest()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, template_folder=SCRIPT_DIR)

_jobs = {}

# ===================== ROUTES =====================
@app.route("/")
def index():
    return send_from_directory(SCRIPT_DIR, "index.html")

@app.route("/favicon.svg")
def favicon():
    return send_from_directory(SCRIPT_DIR, "favicon.svg")

# ===================== AUTH =====================
@app.route("/api/register", methods=["POST"])
def register():
    d = request.json or {}
    accs = jload(ACCS_FILE, {})
    email = d.get("email", "").strip().lower()
    pw = d.get("password", "")
    name = d.get("name", "").strip()
    
    if not email or "@" not in email:
        return jsonify(error="Invalid email"), 400
    if not pw or len(pw) < 6:
        return jsonify(error="Password too short"), 400
    if not name:
        return jsonify(error="Name required"), 400
    if email in accs:
        return jsonify(error="Account already exists"), 409

    accs[email] = {
        "name": name,
        "pw_hash": hashpw(pw),
        "joined": str(datetime.date.today()),
        "method": "email"
    }
    jsave(ACCS_FILE, accs)
    return jsonify(ok=True, name=name, email=email, method="email")

@app.route("/api/login", methods=["POST"])
def login():
    d = request.json or {}
    accs = jload(ACCS_FILE, {})
    email = d.get("email", "").strip().lower()
    pw = d.get("password", "")
    
    if email not in accs or accs[email].get("pw_hash") != hashpw(pw):
        return jsonify(error="Invalid email or password"), 401
    
    u = accs[email]
    return jsonify(ok=True, name=u["name"], email=email, method=u.get("method", "email"))

@app.route("/api/google-login", methods=["POST"])
def google_login():
    d = request.json or {}
    accs = jload(ACCS_FILE, {})
    email = d.get("email", "").strip().lower()
    
    if not email or "@" not in email:
        return jsonify(error="Invalid Gmail"), 400
    
    if email not in accs:
        gname = email.split("@")[0].replace(".", " ").title()
        accs[email] = {"name": gname, "pw_hash": "", "joined": str(datetime.date.today()), "method": "google"}
        jsave(ACCS_FILE, accs)
    
    u = accs[email]
    return jsonify(ok=True, name=u["name"], email=email, method="google")

# ===================== DOWNLOAD =====================
@app.route("/api/download", methods=["POST"])
def start_download():
    d = request.json or {}
    url = d.get("url", "").strip()
    user = d.get("user", "")

    if not url:
        return jsonify(error="No URL provided"), 400

    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {"status":"starting", "progress":0, "speed":"", "eta":"", "log":[], "title":"", "done":False, "filename":""}

    def run():
        job = _jobs[job_id]
        try:
            job["status"] = "downloading"
            job["log"].append("Starting download...")

            def progress_hook(d):
                if d['status'] == 'downloading':
                    job["progress"] = float(d.get('_percent_str', '0').replace('%','')) / 100
                    job["speed"] = d.get('_speed_str', '')
                    job["eta"] = d.get('_eta_str', '')

            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'ffmpeg_location': FFMPEG,
                'merge_output_format': 'mp4',
                'format': 'bestvideo+bestaudio/best',
                'noplaylist': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                job["title"] = info.get('title', 'Unknown')

                ydl.download([url])

            # Find the downloaded file
            files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(job["title"][:30])]
            if files:
                job["filename"] = files[0]

            job["status"] = "done"
            job["progress"] = 1.0
            job["done"] = True
            job["log"].append("Download completed!")

            # Save to history
            hist = jload(HIST_FILE, [])
            hist.append({
                "user": user,
                "title": job["title"],
                "url": url,
                "filename": job["filename"],
                "time": str(datetime.datetime.now())
            })
            jsave(HIST_FILE, hist[-100:])

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

@app.route("/api/history")
def get_history():
    email = request.args.get("user", "")
    hist = jload(HIST_FILE, [])
    mine = [h for h in hist if h.get("user") == email]
    return jsonify(mine[-50:])

@app.route("/downloads/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("\n" + "="*70)
    print("   🎥 YouTube Downloader Web App  -  FIXED & READY")
    print("="*70)
    print(f"   Local:     http://localhost:5000")
    print(f"   Network:   http://{local_ip}:5000")
    print("="*70)
    print("Keep this terminal open while using the app.\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
