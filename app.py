#!/usr/bin/env python3
"""
YouTube Downloader — Web Server
Run this, then open http://localhost:5000
Anyone on your local network can use: http://YOUR_IP:5000
"""
import subprocess, sys, os

def pip(pkg):
    subprocess.check_call([sys.executable,"-m","pip","install",pkg,"-q"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for p,i in [("flask","flask"),("yt-dlp","yt_dlp"),("static-ffmpeg","static_ffmpeg")]:
    try: __import__(i)
    except: print(f"Installing {p}..."); pip(p)

from flask import Flask, request, jsonify, Response, send_from_directory
import yt_dlp, static_ffmpeg, shutil, json, hashlib, datetime
import threading, uuid, re, time, socket

static_ffmpeg.add_paths()
FFMPEG = shutil.which("ffmpeg") or ""

APP_DIR   = os.path.join(os.path.expanduser("~"), ".ytdl_app")
ACCS_FILE = os.path.join(APP_DIR, "accounts.json")
HIST_FILE = os.path.join(APP_DIR, "history.json")
os.makedirs(APP_DIR, exist_ok=True)

def jload(p, d):
    try:
        with open(p) as f: return json.load(f)
    except: return d
def jsave(p, d):
    with open(p,"w") as f: json.dump(d, f, indent=2)
def hashpw(pw): return hashlib.sha256(pw.encode()).hexdigest()

# Get local IP for network sharing
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: return "localhost"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, template_folder=SCRIPT_DIR)
_jobs = {}   # {job_id: {status, progress, speed, eta, log, title, error, done}}

# ── Static files ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(SCRIPT_DIR, "index.html")

@app.route("/favicon.svg")
def favicon():
    return send_from_directory(SCRIPT_DIR, "favicon.svg")

# ── Auth ──────────────────────────────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    d     = request.json or {}
    accs  = jload(ACCS_FILE, {})
    email = d.get("email","").strip().lower()
    pw    = d.get("password","")
    name  = d.get("name","").strip()
    if not email or "@" not in email:
        return jsonify(error="Invalid email address"), 400
    if not pw or len(pw) < 6:
        return jsonify(error="Password must be at least 6 characters"), 400
    if not name:
        return jsonify(error="Name is required"), 400
    if email in accs:
        return jsonify(error="An account with this email already exists"), 409
    accs[email] = {
        "name": name, "pw_hash": hashpw(pw),
        "joined": str(datetime.date.today()), "method": "email",
        "prefs": {}
    }
    jsave(ACCS_FILE, accs)
    return jsonify(ok=True, name=name, email=email, method="email",
                   prefs=accs[email].get("prefs", {}))

@app.route("/api/login", methods=["POST"])
def login():
    d     = request.json or {}
    accs  = jload(ACCS_FILE, {})
    email = d.get("email","").strip().lower()
    pw    = d.get("password","")
    if email not in accs:
        return jsonify(error="No account found with this email"), 404
    if accs[email].get("pw_hash") != hashpw(pw):
        return jsonify(error="Incorrect password"), 401
    u = accs[email]
    return jsonify(ok=True, name=u["name"], email=email,
                   method=u.get("method","email"),
                   prefs=u.get("prefs", {}))

@app.route("/api/google-login", methods=["POST"])
def google_login():
    d     = request.json or {}
    accs  = jload(ACCS_FILE, {})
    email = d.get("email","").strip().lower()
    if not email or "@" not in email:
        return jsonify(error="Enter a valid Gmail address"), 400
    if email not in accs:
        gname = email.split("@")[0].replace(".", " ").title()
        accs[email] = {
            "name": gname, "pw_hash": "",
            "joined": str(datetime.date.today()), "method": "google",
            "prefs": {}
        }
        jsave(ACCS_FILE, accs)
    u = accs[email]
    return jsonify(ok=True, name=u["name"], email=email,
                   method=u.get("method","google"),
                   prefs=u.get("prefs", {}))

# ── Preferences ───────────────────────────────────────────────────────────────
@app.route("/api/prefs", methods=["GET"])
def get_prefs():
    email = request.args.get("user","").strip().lower()
    accs  = jload(ACCS_FILE, {})
    if email not in accs:
        return jsonify(prefs={}), 200
    return jsonify(prefs=accs[email].get("prefs", {}))

@app.route("/api/prefs", methods=["POST"])
def save_prefs():
    d     = request.json or {}
    email = d.get("user","").strip().lower()
    prefs = d.get("prefs", {})
    accs  = jload(ACCS_FILE, {})
    if email not in accs:
        return jsonify(error="User not found"), 404
    accs[email]["prefs"] = prefs
    jsave(ACCS_FILE, accs)
    return jsonify(ok=True)

# ── History ───────────────────────────────────────────────────────────────────
@app.route("/api/history")
def get_history():
    email = request.args.get("user","")
    hist  = jload(HIST_FILE, [])
    mine  = [h for h in hist if h.get("user")==email]
    return jsonify(mine[-80:])

@app.route("/api/history/clear", methods=["DELETE"])
def clear_history():
    email = request.args.get("user","")
    hist  = [h for h in jload(HIST_FILE,[]) if h.get("user")!=email]
    jsave(HIST_FILE, hist)
    return jsonify(ok=True)

# ── Download ──────────────────────────────────────────────────────────────────
@app.route("/api/download", methods=["POST"])
def start_download():
    d       = request.json or {}
    url     = d.get("url","").strip()
    mode    = d.get("mode","Video")
    quality = d.get("quality","Best (Max Quality)")
    fmt     = d.get("format","mp4")
    savepath= d.get("path","").strip() or os.path.join(os.path.expanduser("~"),"Downloads")
    user    = d.get("user","")

    if not url:
        return jsonify(error="No URL provided"), 400

    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {
        "status":"starting","progress":0,"speed":"","eta":"",
        "log":[],"title":"","error":None,"done":False
    }

    def run():
        job = _jobs[job_id]
        q_map = {
            "Best (Max Quality)": "bestvideo+bestaudio/best",
            "4K":                 "bestvideo[height<=2160]+bestaudio/best",
            "1080p":              "bestvideo[height<=1080]+bestaudio/best",
            "720p":               "bestvideo[height<=720]+bestaudio/best",
            "480p":               "bestvideo[height<=480]+bestaudio/best",
            "360p":               "bestvideo[height<=360]+bestaudio/best",
        }
        is_audio    = "Audio" in mode
        is_playlist = "Playlist" in mode
        os.makedirs(savepath, exist_ok=True)
        out_tmpl = os.path.join(savepath, "%(title)s.%(ext)s")

        opts = {
            "outtmpl":        out_tmpl,
            "noplaylist":     not is_playlist,
            "quiet":          True,
            "no_warnings":    True,
            "ignoreerrors":   True,
            "progress_hooks": [lambda d: _hook(job, d)],
        }
        if FFMPEG:
            opts["ffmpeg_location"] = os.path.dirname(FFMPEG)

        if is_audio:
            ext = fmt if fmt in ("mp3","m4a") else "mp3"
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [{
                "key":"FFmpegExtractAudio",
                "preferredcodec":ext,"preferredquality":"320"
            }]
        else:
            opts["format"] = q_map.get(quality,"bestvideo+bestaudio/best")
            opts["merge_output_format"] = fmt if fmt in ("mp4","mkv","webm") else "mp4"

        title = url
        try:
            with yt_dlp.YoutubeDL({"quiet":True,"no_warnings":True}) as y:
                try:
                    info  = y.extract_info(url, download=False)
                    title = info.get("title", url)[:80]
                    job["title"] = title
                    job["log"].append({"text": title, "type":"dim"})
                except: pass

            job["status"] = "downloading"
            with yt_dlp.YoutubeDL(opts) as y:
                y.download([url])

            job["status"]   = "done"
            job["progress"] = 100
            job["done"]     = True
            job["log"].append({"text": f"✔  Saved to: {savepath}", "type":"success"})

            hist = jload(HIST_FILE, [])
            hist.append({
                "user":user,"url":url,"title":title,
                "mode":mode,"quality":quality,"format":fmt,"status":"done",
                "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            jsave(HIST_FILE, hist)

        except Exception as e:
            job["status"] = "error"
            job["error"]  = str(e)
            job["done"]   = True
            job["log"].append({"text":f"✖  {e}","type":"error"})
            hist = jload(HIST_FILE, [])
            hist.append({
                "user":user,"url":url,"title":title,
                "mode":mode,"quality":quality,"format":fmt,"status":"error",
                "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            jsave(HIST_FILE, hist)

    threading.Thread(target=run, daemon=True).start()
    return jsonify(job_id=job_id)

def _hook(job, d):
    if d["status"] == "downloading":
        raw = d.get("_percent_str","0%").strip()
        pct = float(re.sub(r"[^\d.]","",raw) or 0)
        job["progress"] = pct
        job["speed"]    = d.get("_speed_str","").strip()
        job["eta"]      = d.get("_eta_str","").strip()
    elif d["status"] == "finished":
        job["status"] = "merging"
        job["log"].append({"text":"Merging video + audio…","type":"dim"})

@app.route("/api/progress/<job_id>")
def progress(job_id):
    def stream():
        last_log = 0
        while True:
            job = _jobs.get(job_id)
            if not job:
                yield f"data: {json.dumps({'error':'not found'})}\n\n"; break
            new_logs  = job["log"][last_log:]
            last_log  = len(job["log"])
            yield f"data: {json.dumps({'status':job['status'],'progress':job['progress'],'speed':job['speed'],'eta':job['eta'],'title':job['title'],'new_logs':new_logs,'done':job['done'],'error':job['error']})}\n\n"
            if job["done"]: break
            time.sleep(0.35)
    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@app.route("/api/ytdlp-version")
def ytdlp_version():
    return jsonify(version=yt_dlp.version.__version__, ffmpeg=bool(FFMPEG))

@app.route("/api/update-ytdlp", methods=["POST"])
def update_ytdlp():
    try:
        subprocess.check_output(
            [sys.executable,"-m","pip","install","--upgrade","yt-dlp"],
            stderr=subprocess.STDOUT)
        import importlib
        importlib.reload(yt_dlp)
        return jsonify(ok=True, message=f"Updated! Now on v{yt_dlp.version.__version__}")
    except Exception as e:
        return jsonify(ok=False, message=str(e))

if __name__ == "__main__":
    import webbrowser
    local_ip = get_local_ip()
    print("\n" + "═"*52)
    print("  ▶  YouTube Downloader — Web Server")
    print("═"*52)
    print(f"  Local:    http://localhost:5000")
    print(f"  Network:  http://{local_ip}:5000")
    print("  (Share the Network link with others on your WiFi)")
    print("═"*52 + "\n")
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
