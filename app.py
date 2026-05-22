#!/usr/bin/env python3
"""
IDL — Internet Downloader
Fast · Private · Unlimited
Supports 1000+ sites via yt-dlp
Run this file, browser opens automatically.
"""
import subprocess, sys, os

def pip(pkg):
    subprocess.check_call([sys.executable,"-m","pip","install",pkg,"-q"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for p,i in [("flask","flask"),("yt-dlp","yt_dlp"),("static-ffmpeg","static_ffmpeg")]:
    try: __import__(i)
    except: print(f"  Installing {p}..."); pip(p)

from flask import Flask, request, jsonify, Response, send_from_directory
import yt_dlp, static_ffmpeg, shutil, json, hashlib, datetime
import threading, uuid, re, time, socket, webbrowser

static_ffmpeg.add_paths()
FFMPEG = shutil.which("ffmpeg") or ""

# ── Storage ───────────────────────────────────────────────────────────────────
APP_DIR   = os.path.join(os.path.expanduser("~"), ".idl_app")
ACCS_FILE = os.path.join(APP_DIR, "accounts.json")
HIST_FILE = os.path.join(APP_DIR, "history.json")
os.makedirs(APP_DIR, exist_ok=True)

def jload(p, d):
    try:
        with open(p) as f: return json.load(f)
    except: return d

def jsave(p, d):
    with open(p,"w") as f: json.dump(d, f, indent=2)

def hashpw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80)); ip=s.getsockname()[0]; s.close(); return ip
    except: return "localhost"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, template_folder=SCRIPT_DIR)
_jobs = {}

# ── Static ────────────────────────────────────────────────────────────────────
@app.route("/")
def index(): return send_from_directory(SCRIPT_DIR, "index.html")

@app.route("/favicon.svg")
def favicon(): return send_from_directory(SCRIPT_DIR, "favicon.svg")

# ── Auth ──────────────────────────────────────────────────────────────────────
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
    accs[email]={"name":name,"pw_hash":hashpw(pw),
                 "joined":str I need to complete the Python file that was cut off. Let me continue with the rest of the backend code.
