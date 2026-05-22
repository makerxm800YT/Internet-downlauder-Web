#!/usr/bin/env python3
"""
IDLR — Internet Downloader
YouTube · Spotify · SoundCloud · Twitter · Instagram · TikTok and more
Fast · Private · Unlimited
"""
import subprocess, sys, os

def pip(pkg):
    subprocess.check_call([sys.executable,"-m","pip","install",pkg,"-q"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for p,i in [("flask","flask"),("yt-dlp","yt_dlp"),("static-ffmpeg","static_ffmpeg"),("spotdl","spotdl")]:
    try: __import__(i)
    except: print(f"  Installing {p}..."); pip(p)

from flask import Flask, request, jsonify, Response, send_from_directory
import yt_dlp, static_ffmpeg, shutil, json, hashlib, datetime, base64
import threading, uuid, re, time, socket, webbrowser

static_ffmpeg.add_paths()
FFMPEG = shutil.which("ffmpeg") or ""

# ── Storage ───────────────────────────────────────────────────────────────────
APP_DIR   = os.path.join(os.path.expanduser("~"), ".idlr_app")
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

def local_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80)); ip=s.getsockname()[0]; s.close(); return ip
    except: return "localhost"

def is_spotify(url):
    return "spotify.com" in url or url.startswith("spotify:")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, template_folder=SCRIPT_DIR)
_jobs = {}

# ── Static ────────────────────────────────────────────────────────────────────
@app.route("/")
def index(): return send_from_directory(SCRIPT_DIR, "index.html")

@app.route("/favicon.svg")
def favicon(): return send_from_directory(SCRIPT_DIR, "favicon.svg")

# ── Auth ──────────────────────────────────────────────────────────────────────
def _user_resp(email, u):
    return jsonify(ok=True, name=u["name"], email=email,
                   username=u.get("username",""),
                   bio=u.get("bio",""),
                   avatar=u.get("avatar",""),
                   method=u.get("method","email"),
                   prefs=u.get("prefs",{}),
                   joined=u.get("joined",""))

@app.route("/api/register", methods=["POST"])
def register():
    d=request.json or {}
    accs=jload(ACCS_FILE,{})
    email=d.get("email","").strip().lower()
    pw=d.get("password",""); name=d.get("name","").strip()
    if not email or "@" not in email: return jsonify(error="Invalid email"),400
    if not pw or len(pw)<6: return jsonify(error="Password must be 6+ characters"),400
    if not name: return jsonify(error="Name required"),400
    if email in accs: return jsonify(error="Account already exists"),409
    accs[email]={"name":name,"pw_hash":hashpw(pw),"joined":str(datetime.date.today()),
                 "method":"email","prefs":{},"username":"","bio":"","avatar":""}
    jsave(ACCS_FILE,accs)
    return _user_resp(email, accs[email])

@app.route("/api/login", methods=["POST"])
def login():
    d=request.json or {}
    accs=jload(ACCS_FILE,{})
    email=d.get("email","").strip().lower(); pw=d.get("password","")
    if email not in accs: return jsonify(error="No account with this email"),404
    if accs[email].get("pw_hash")!=hashpw(pw): return jsonify(error="Wrong password"),401
    return _user_resp(email, accs[email])

@app.route("/api/google-login", methods=["POST"])
def google_login():
    d=request.json or {}
    accs=jload(ACCS_FILE,{})
    email=d.get("email","").strip().lower()
    if not email or "@" not in email: return jsonify(error="Invalid Gmail"),400
    if email not in accs:
        gname=email.split("@")[0].replace("."," ").title()
        accs[email]={"name":gname,"pw_hash":"","joined":str(datetime.date.today()),
                     "method":"google","prefs":{},"username":"","bio":"","avatar":""}
        jsave(ACCS_FILE,accs)
    return _user_resp(email, accs[email])

# ── Profile update ────────────────────────────────────────────────────────────
@app.route("/api/profile", methods=["POST"])
def update_profile():
    d=request.json or {}
    email=d.get("user","").strip().lower()
    accs=jload(ACCS_FILE,{})
    if email not in accs: return jsonify(error="User not found"),404
    u=accs[email]
    if "name"     in d and d["name"].strip():     u["name"]     = d["name"].strip()[:40]
    if "username" in d:                            u["username"] = d["username"].strip()[:24]
    if "bio"      in d:                            u["bio"]      = d["bio"].strip()[:160]
    if "avatar"   in d:                            u["avatar"]   = d["avatar"]  # base64 data-url
    jsave(ACCS_FILE,accs)
    return _user_resp(email, u)

# ── Prefs ─────────────────────────────────────────────────────────────────────
@app.route("/api/prefs", methods=["POST"])
def save_prefs():
    d=request.json or {}
    email=d.get("user","").strip().lower(); prefs=d.get("prefs",{})
    accs=jload(ACCS_FILE,{})
    if email not in accs: return jsonify(error="User not found"),404
    accs[email]["prefs"]=prefs; jsave(ACCS_FILE,accs)
    return jsonify(ok=True)

# ── History ───────────────────────────────────────────────────────────────────
@app.route("/api/history")
def get_history():
    email=request.args.get("user","")
    hist=jload(HIST_FILE,[])
    return jsonify([h for h in hist if h.get("user")==email][-80:])

@app.route("/api/history/clear", methods=["DELETE"])
def clear_history():
    email=request.args.get("user","")
    jsave(HIST_FILE,[h for h in jload(HIST_FILE,[]) if h.get("user")!=email])
    return jsonify(ok=True)

@app.route("/api/history/remove", methods=["DELETE"])
def remove_history_item():
    d=request.json or {}
    email=d.get("user",""); url=d.get("url","")
    hist=[h for h in jload(HIST_FILE,[])
          if not(h.get("user")==email and h.get("url")==url)]
    jsave(HIST_FILE,hist)
    return jsonify(ok=True)

# ── Spotify download via spotdl ───────────────────────────────────────────────
def _spotify_run(job, url, savepath, user, fmt):
    """Download Spotify track/album/playlist using spotdl (finds on YouTube, no DRM)"""
    os.makedirs(savepath, exist_ok=True)
    job["log"].append({"t":"Detected Spotify link — using spotdl…","c":"dim"})
    job["status"]="downloading"

    title = url
    thumb = ""

    # Try to get metadata first via spotdl
    try:
        import spotdl
        from spotdl import Spotdl
        from spotdl.types.song import Song
        try:
            songs = Song.from_url(url)
            if isinstance(songs, list): songs = songs[:1]
            else: songs = [songs]
            if songs:
                title = songs[0].display_name or url
                thumb = songs[0].cover_url or ""
                job["title"] = title
                job["thumb"] = thumb
                job["log"].append({"t": title, "c":"dim"})
        except Exception: pass
    except Exception: pass

    audio_fmt = fmt if fmt in ("mp3","m4a","opus","ogg","flac") else "mp3"

    try:
        result = subprocess.run(
            [sys.executable, "-m", "spotdl",
             "--output", savepath,
             "--format", audio_fmt,
             "--bitrate", "320k",
             url],
            capture_output=True, text=True, timeout=600
        )
        out = (result.stdout or "") + (result.stderr or "")
        # Parse spotdl output for title
        for line in out.split("\n"):
            if "Downloaded" in line or "Skipping" in line:
                job["log"].append({"t": line.strip(), "c":"ok"})
            elif "Error" in line or "Failed" in line:
                job["log"].append({"t": line.strip(), "c":"err"})

        if result.returncode == 0 or "Downloaded" in out:
            job.update({"status":"done","progress":100,"done":True})
            job["log"].append({"t":f"✓ Spotify download saved to {savepath}","c":"ok"})
            _save_hist(user, url, title, thumb, "Spotify", "Audio", audio_fmt, "done")
        else:
            raise Exception(out[-300:] if out else "spotdl failed")
    except subprocess.TimeoutExpired:
        raise Exception("Download timed out after 10 minutes")

# ── Generic yt-dlp download ───────────────────────────────────────────────────
def _ytdlp_run(job, url, mode, quality, fmt, savepath, user):
    q_map={
        "Best (Max Quality)":"bestvideo+bestaudio/best",
        "4K":"bestvideo[height<=2160]+bestaudio/best",
        "1080p":"bestvideo[height<=1080]+bestaudio/best",
        "720p":"bestvideo[height<=720]+bestaudio/best",
        "480p":"bestvideo[height<=480]+bestaudio/best",
        "360p":"bestvideo[height<=360]+bestaudio/best",
    }
    os.makedirs(savepath, exist_ok=True)
    opts={
        "outtmpl":os.path.join(savepath,"%(title)s.%(ext)s"),
        "noplaylist":"Playlist" not in mode,
        "quiet":True,"no_warnings":True,"ignoreerrors":True,
        "progress_hooks":[lambda d:_hook(job,d)],
    }
    if FFMPEG: opts["ffmpeg_location"]=os.path.dirname(FFMPEG)
    if "Audio" in mode or fmt in ("mp3","m4a"):
        ext=fmt if fmt in("mp3","m4a") else "mp3"
        opts["format"]="bestaudio/best"
        opts["postprocessors"]=[{"key":"FFmpegExtractAudio",
                                 "preferredcodec":ext,"preferredquality":"320"}]
    else:
        opts["format"]=q_map.get(quality,"bestvideo+bestaudio/best")
        opts["merge_output_format"]=fmt if fmt in("mp4","mkv","webm") else "mp4"

    title=url; thumb=""
    try:
        with yt_dlp.YoutubeDL({"quiet":True,"no_warnings":True}) as y:
            try:
                info=y.extract_info(url,download=False)
                title=info.get("title",url)[:80]
                thumb=info.get("thumbnail","")
                job["title"]=title; job["thumb"]=thumb
                job["log"].append({"t":title,"c":"dim"})
            except: pass
        job["status"]="downloading"
        with yt_dlp.YoutubeDL(opts) as y:
            y.download([url])
        job.update({"status":"done","progress":100,"done":True})
        job["log"].append({"t":f"✓ Saved to {savepath}","c":"ok"})
        _save_hist(user, url, title, thumb, mode, quality, fmt, "done")
    except Exception as e:
        job.update({"status":"error","error":str(e),"done":True})
        job["log"].append({"t":f"✗ {e}","c":"err"})
        _save_hist(user, url, title, thumb, mode, quality, fmt, "error")

def _save_hist(user, url, title, thumb, mode, quality, fmt, status):
    hist=jload(HIST_FILE,[])
    entry={"user":user,"url":url,"title":title,"thumb":thumb,"mode":mode,
           "quality":quality,"format":fmt,"status":status,
           "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    hist=[h for h in hist if not(h.get("user")==user and h.get("url")==url)]
    hist.append(entry)
    jsave(HIST_FILE,hist)

# ── Download endpoint ─────────────────────────────────────────────────────────
@app.route("/api/download", methods=["POST"])
def start_download():
    d=request.json or {}
    url=d.get("url","").strip(); mode=d.get("mode","Video")
    quality=d.get("quality","Best (Max Quality)"); fmt=d.get("format","mp4")
    savepath=d.get("path","").strip() or os.path.join(os.path.expanduser("~"),"Downloads")
    user=d.get("user","")
    if not url: return jsonify(error="No URL"),400

    jid=str(uuid.uuid4())[:8]
    _jobs[jid]={"status":"starting","progress":0,"speed":"","eta":"",
                "log":[],"title":"","thumb":"","error":None,"done":False}

    def run():
        job=_jobs[jid]
        try:
            if is_spotify(url):
                _spotify_run(job, url, savepath, user, fmt)
            else:
                _ytdlp_run(job, url, mode, quality, fmt, savepath, user)
        except Exception as e:
            job.update({"status":"error","error":str(e),"done":True})
            job["log"].append({"t":f"✗ {e}","c":"err"})

    threading.Thread(target=run, daemon=True).start()
    return jsonify(job_id=jid)

def _hook(job, d):
    if d["status"]=="downloading":
        raw=d.get("_percent_str","0%").strip()
        pct=float(re.sub(r"[^\d.]","",raw) or 0)
        job.update({"progress":pct,"speed":d.get("_speed_str","").strip(),
                    "eta":d.get("_eta_str","").strip()})
    elif d["status"]=="finished":
        job["status"]="merging"
        job["log"].append({"t":"Merging…","c":"dim"})

@app.route("/api/progress/<jid>")
def progress(jid):
    def stream():
        ll=0
        while True:
            job=_jobs.get(jid)
            if not job: yield f"data:{json.dumps({'error':'not found'})}\n\n"; break
            new=job["log"][ll:]; ll=len(job["log"])
            yield f"data:{json.dumps({'status':job['status'],'progress':job['progress'],'speed':job['speed'],'eta':job['eta'],'title':job['title'],'thumb':job.get('thumb',''),'logs':new,'done':job['done'],'error':job['error']})}\n\n"
            if job["done"]: break
            time.sleep(0.3)
    return Response(stream(),mimetype="text/event-stream",
                    headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@app.route("/api/info")
def info():
    return jsonify(ytdlp=yt_dlp.version.__version__,
                   ffmpeg=bool(FFMPEG),
                   network=f"http://{local_ip()}:5000")

@app.route("/api/update-ytdlp", methods=["POST"])
def update_ytdlp():
    try:
        subprocess.check_output([sys.executable,"-m","pip","install","--upgrade","yt-dlp","spotdl"],
                                 stderr=subprocess.STDOUT)
        import importlib; importlib.reload(yt_dlp)
        return jsonify(ok=True,msg=f"Updated! yt-dlp v{yt_dlp.version.__version__}")
    except Exception as e:
        return jsonify(ok=False,msg=str(e))

if __name__=="__main__":
    ip=local_ip()
    print("\n"+"━"*54)
    print("  IDLR — Internet Downloader")
    print("  YouTube · Spotify · SoundCloud · and more")
    print("━"*54)
    print(f"  ▸ Local    http://localhost:5000")
    print(f"  ▸ Network  http://{ip}:5000")
    print("━"*54)
    print("  Keep this window open while using the app.")
    print("  Press Ctrl+C to stop.\n")
    threading.Timer(1.4,lambda:webbrowser.open("http://localhost:5000")).start()
    app.run(host="0.0.0.0",port=5000,debug=False,threaded=True)
