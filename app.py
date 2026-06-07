#!/usr/bin/env python3
"""
IDLR — Internet Downloader
YouTube · Spotify · SoundCloud · TikTok · Instagram and more
"""
import subprocess
import sys
import os
import logging

logging.getLogger("flask").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)


def pip(pkg):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", pkg, "-q"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


for pkg, mod in [
    ("flask", "flask"),
    ("yt-dlp", "yt_dlp"),
    ("static-ffmpeg", "static_ffmpeg"),
    ("spotdl", "spotdl"),
]:
    try:
        __import__(mod)
    except ImportError:
        print(f"  Installing {pkg}...")
        pip(pkg)

from flask import Flask, request, jsonify, Response, send_from_directory
import yt_dlp
import static_ffmpeg
import shutil
import json
import datetime
import threading
import uuid
import re
import time
import socket
import webbrowser

static_ffmpeg.add_paths()
FFMPEG = shutil.which("ffmpeg") or ""

APP_DIR = os.path.join(os.path.expanduser("~"), ".idlr_app")
HIST_FILE = os.path.join(APP_DIR, "history.json")
LOCAL_USER = "local"
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, template_folder=SCRIPT_DIR)
_jobs = {}
_jobs_lock = threading.Lock()


def jload(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        if os.path.exists(path):
            try:
                os.replace(path, path + ".bak")
            except OSError:
                pass
        return default


def jsave(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def fix_path(path):
    """Turn ~/Downloads or %USERPROFILE%\\Downloads into a real folder."""
    if not path:
        return DOWNLOADS_DIR
    path = os.path.expandvars(path.strip())
    path = os.path.expanduser(path)
    return path


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "localhost"


def is_spotify(url):
    return "spotify.com" in url or url.startswith("spotify:")


@app.route("/")
def index():
    return send_from_directory(SCRIPT_DIR, "index.html")


@app.route("/favicon.svg")
def favicon():
    return send_from_directory(SCRIPT_DIR, "favicon.svg")


@app.route("/api/history")
def get_history():
    hist = jload(HIST_FILE, [])
    return jsonify(hist[-80:])


@app.route("/api/history/clear", methods=["DELETE"])
def clear_history():
    jsave(HIST_FILE, [])
    return jsonify(ok=True)


@app.route("/api/history/remove", methods=["DELETE"])
def remove_history_item():
    data = request.json or {}
    url = data.get("url", "")
    hist = [h for h in jload(HIST_FILE, []) if h.get("url") != url]
    jsave(HIST_FILE, hist)
    return jsonify(ok=True)


def _save_hist(user, url, title, thumb, mode, quality, fmt, status):
    hist = jload(HIST_FILE, [])
    entry = {
        "user": user,
        "url": url,
        "title": title,
        "thumb": thumb,
        "mode": mode,
        "quality": quality,
        "format": fmt,
        "status": status,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    hist = [h for h in hist if not (h.get("user") == user and h.get("url") == url)]
    hist.append(entry)
    jsave(HIST_FILE, hist)


def _spotify_run(job, url, savepath, user, fmt):
    os.makedirs(savepath, exist_ok=True)
    job["log"].append({"t": "Spotify — downloading audio...", "c": "dim"})
    job["status"] = "downloading"

    title = url
    thumb = ""

    try:
        from spotdl.types.song import Song

        songs = Song.from_url(url)
        if isinstance(songs, list):
            songs = songs[:1]
        else:
            songs = [songs]
        if songs:
            title = songs[0].display_name or url
            thumb = songs[0].cover_url or ""
            job["title"] = title
            job["thumb"] = thumb
            job["log"].append({"t": title, "c": "dim"})
    except Exception as e:
        job["log"].append({"t": f"Metadata warning: {str(e)[:50]}", "c": "dim"})

    audio_fmt = fmt if fmt in ("mp3", "m4a", "opus", "ogg", "flac") else "mp3"

    job["log"].append({"t": f"Downloading as {audio_fmt.upper()}...", "c": "dim"})
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "spotdl",
            "--output",
            savepath,
            "--format",
            audio_fmt,
            "--bitrate",
            "320k",
            url,
        ],
        capture_output=True,
        text=True,
        timeout=900,
    )
    out = (result.stdout or "") + (result.stderr or "")

    if "Error" in out or "Failed" in out:
        for line in out.split("\n"):
            line = line.strip()
            if line and ("Error" in line or "Failed" in line):
                job["log"].append({"t": line[:120], "c": "err"})
                break

    if result.returncode == 0 or "Downloaded" in out or "Skipping" in out:
        job.update({"status": "done", "progress": 100, "done": True})
        job["log"].append({"t": "Download complete!", "c": "ok"})
        _save_hist(LOCAL_USER, url, title, thumb, "Spotify", "Audio", audio_fmt, "done")
    else:
        raise RuntimeError(f"spotdl failed (code {result.returncode})")


def _ytdlp_run(job, url, mode, quality, fmt, savepath, user):
    q_map = {
        "Best (Max Quality)": "bestvideo+bestaudio/best",
        "8K": "bestvideo[height<=4320]+bestaudio/best",
        "4K": "bestvideo[height<=2160]+bestaudio/best",
        "1440p": "bestvideo[height<=1440]+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best",
        "720p": "bestvideo[height<=720]+bestaudio/best",
        "480p": "bestvideo[height<=480]+bestaudio/best",
        "360p": "bestvideo[height<=360]+bestaudio/best",
        "240p": "bestvideo[height<=240]+bestaudio/best",
        "144p": "bestvideo[height<=144]+bestaudio/best",
    }
    bitrate_map = {"320k": "320", "256k": "256", "192k": "192", "128k": "128", "96k": "96"}

    os.makedirs(savepath, exist_ok=True)

    opts = {
        "outtmpl": os.path.join(savepath, "%(title)s.%(ext)s"),
        "noplaylist": "Playlist" not in mode,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [lambda d: _hook(job, d)],
        "socket_timeout": 30,
        "extractor_args": {"youtube": {"player_client": ["web"]}},
    }

    if FFMPEG:
        opts["ffmpeg_location"] = os.path.dirname(FFMPEG)

    if "Audio" in mode or fmt in ("mp3", "m4a", "flac", "wav", "opus"):
        ext = fmt if fmt in ("mp3", "m4a", "flac", "wav", "opus") else "mp3"
        br = bitrate_map.get(quality, "320")
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": ext, "preferredquality": br}
        ]
    else:
        opts["format"] = q_map.get(quality, "bestvideo+bestaudio/best")
        opts["merge_output_format"] = fmt if fmt in ("mp4", "mkv", "webm") else "mp4"

    title = url
    thumb = ""

    job["log"].append({"t": "Fetching info...", "c": "dim"})
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", url)[:80]
            thumb = info.get("thumbnail", "")
            job["title"] = title
            job["thumb"] = thumb
            job["log"].append({"t": title, "c": "dim"})
    except Exception as e:
        job["log"].append({"t": f"Metadata warning: {str(e)[:60]}", "c": "dim"})

    job["status"] = "downloading"
    job["log"].append({"t": f"Downloading ({quality})...", "c": "dim"})

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    job.update({"status": "done", "progress": 100, "done": True})
    job["log"].append({"t": "Download complete!", "c": "ok"})
    job["log"].append({"t": f"Saved to {savepath}", "c": "ok"})
    _save_hist(LOCAL_USER, url, title, thumb, mode, quality, fmt, "done")


@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.json or {}
    url = data.get("url", "").strip()
    mode = data.get("mode", "Video")
    quality = data.get("quality", "Best (Max Quality)")
    fmt = data.get("format", "mp4")
    savepath = fix_path(data.get("path", ""))
    if not url:
        return jsonify(error="No URL provided"), 400
    if not url.startswith(("http://", "https://", "spotify:")):
        return jsonify(error="Invalid URL format"), 400

    jid = str(uuid.uuid4())[:8]
    with _jobs_lock:
        _jobs[jid] = {
            "status": "starting",
            "progress": 0,
            "speed": "",
            "eta": "",
            "log": [],
            "title": "",
            "thumb": "",
            "error": None,
            "done": False,
        }

    def run():
        job = _jobs[jid]
        try:
            job["log"].append({"t": "Starting download...", "c": "dim"})
            if is_spotify(url):
                _spotify_run(job, url, savepath, LOCAL_USER, fmt)
            else:
                _ytdlp_run(job, url, mode, quality, fmt, savepath, LOCAL_USER)
        except Exception as e:
            err_msg = str(e)[:150]
            job.update({"status": "error", "error": err_msg, "done": True})
            job["log"].append({"t": err_msg, "c": "err"})

    threading.Thread(target=run, daemon=True).start()
    return jsonify(job_id=jid)


def _hook(job, d):
    if d["status"] == "downloading":
        raw = d.get("_percent_str", "0%").strip()
        pct = float(re.sub(r"[^\d.]", "", raw) or 0)
        with _jobs_lock:
            job.update(
                {
                    "progress": pct,
                    "speed": d.get("_speed_str", "").strip(),
                    "eta": d.get("_eta_str", "").strip(),
                }
            )
    elif d["status"] == "finished":
        with _jobs_lock:
            job["status"] = "post-processing"
            job["log"].append({"t": "Post-processing...", "c": "dim"})


@app.route("/api/progress/<jid>")
def progress(jid):
    def stream():
        last = 0
        while True:
            with _jobs_lock:
                job = _jobs.get(jid)
            if not job:
                yield f"data:{json.dumps({'error': 'not found'})}\n\n"
                break
            with _jobs_lock:
                new_logs = job["log"][last:]
                last = len(job["log"])
                payload = {
                    "status": job["status"],
                    "progress": job["progress"],
                    "speed": job["speed"],
                    "eta": job["eta"],
                    "title": job["title"],
                    "thumb": job.get("thumb", ""),
                    "logs": new_logs,
                    "done": job["done"],
                    "error": job.get("error"),
                }
            yield f"data:{json.dumps(payload)}\n\n"
            if job["done"]:
                break
            time.sleep(0.3)

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/info")
def info():
    return jsonify(
        ytdlp=yt_dlp.version.__version__,
        ffmpeg=bool(FFMPEG),
        network=f"http://{local_ip()}:5000",
        downloads=DOWNLOADS_DIR,
    )


@app.route("/api/update-ytdlp", methods=["POST"])
def update_ytdlp():
    try:
        subprocess.check_output(
            [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp", "spotdl"],
            stderr=subprocess.STDOUT,
            timeout=300,
        )
        import importlib

        importlib.reload(yt_dlp)
        return jsonify(ok=True, msg=f"Updated! yt-dlp v{yt_dlp.version.__version__}")
    except Exception as e:
        return jsonify(ok=False, msg=str(e)[:100])


def _run_server():
    ip = local_ip()
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)


if __name__ == "__main__":
    os.chdir(SCRIPT_DIR)

    # Double-click on Windows: restart without a terminal window
    if sys.platform == "win32" and not os.environ.get("IDLR_RUNNING"):
        pyw = sys.executable.replace("python.exe", "pythonw.exe").replace(
            "Python.exe", "pythonw.exe"
        )
        if os.path.isfile(pyw):
            env = os.environ.copy()
            env["IDLR_RUNNING"] = "1"
            subprocess.Popen([pyw, os.path.abspath(__file__)], env=env, cwd=SCRIPT_DIR)
            sys.exit(0)

    _run_server()
