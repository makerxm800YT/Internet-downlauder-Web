#!/usr/bin/env python3
"""
YouTube Downloader Web Server
"""

import subprocess, sys, os

def pip_install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for p in ["flask", "yt-dlp", "static-ffmpeg"]:
    try:
        __import__(p.replace("-", "_"))
    except:
        print(f"Installing {p}...")
        pip_install(p)

from flask import Flask, request, jsonify, Response, send_from_directory
import yt_dlp, static_ffmpeg, shutil, json, hashlib, datetime
import threading, uuid, time, socket

static_ffmpeg.add_paths()

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

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "localhost"

app = Flask(__name__)

_jobs = {}

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ====================== AUTH ======================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    accs = jload(ACCS_FILE, {})
    email = data.get("email","").strip().lower()
    if email in accs:
        return jsonify(error="Account already exists"), 400
    accs[email] = {
        "name": data.get("name"),
        "pw_hash": hashpw(data.get("password")),
        "method": "email"
    }
    jsave(ACCS_FILE, accs)
    return jsonify(ok=True, name=data.get("name"), email=email)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    accs = jload(ACCS_FILE, {})
    email = data.get("email","").strip().lower()
    if email not in accs or accs[email]["pw_hash"] != hashpw(data.get("password")):
        return jsonify(error="Wrong email or password"), 401
    u = accs[email]
    return jsonify(ok=True, name=u["name"], email=email)

@app.route("/api/google-login", methods=["POST"])
def google_login():
    data = request.get_json()
    email = data.get("email","").strip().lower()
    accs = jload(ACCS_FILE, {})
    if email not in accs:
        accs[email] = {"name": email.split("@")[0].title(), "method": "google"}
        jsave(ACCS_FILE, accs)
    u = accs[email]
    return jsonify(ok=True, name=u["name"], email=email)

# ====================== DOWNLOAD ======================
@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.get_json()
    url = data.get("url","").strip()
    if not url:
        return jsonify(error="No URL"), 400

    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {"progress":0, "status":"starting", "log":[], "done":False}

    def run():
        try:
            opts = {
                'outtmpl': '%(title)s.%(ext)s',
                'progress_hooks': [lambda d: update_progress(job_id, d)],
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            _jobs[job_id]["done"] = True
            _jobs[job_id]["status"] = "done"
        except Exception as e:
            _jobs[job_id]["status"] = "error"
            _jobs[job_id]["error"] = str(e)

    threading.Thread(target=run, daemon=True).start()
    return jsonify(job_id=job_id)

def update_progress(job_id, d):
    if d['status'] == 'downloading':
        _jobs[job_id]["progress"] = float(d.get('_percent_str', '0%')[:-1] or 0)

@app.route("/api/progress/<job_id>")
def progress(job_id):
    def stream():
        while True:
            job = _jobs.get(job_id, {})
            yield f"data: {json.dumps(job)}\n\n"
            if job.get("done"):
                break
            time.sleep(0.5)
    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    ip = get_local_ip()
    print("\n" + "="*55)
    print("   🌐 YouTube Downloader WEB")
    print("="*55)
    print(f"   Local:     http://localhost:5000")
    print(f"   Network:   http://{ip}:5000   ← Use this on iPhone")
    print("="*55)
    app.run(host="0.0.0.0", port=5000)
