import subprocess, sys, os, threading, uuid, json, time, socket, webbrowser
from flask import Flask, request, jsonify, Response, send_from_directory

# Core Setup
app = Flask(__name__, static_folder=".", template_folder=".")
_jobs = {}

@app.route("/")
def index(): return send_from_directory(".", "index.html")

@app.route("/api/download", methods=["POST"])
def start_download():
    d = request.json or {}
    url = d.get("url", "").strip()
    is_audio = d.get("is_audio", False)
    quality = d.get("quality", "1080") # Default to 1080p

    if not url: return jsonify(error="No URL provided"), 400

    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {"status":"Initializing", "progress":0, "speed":"", "eta":"", "title":"", "done":False}

    def run():
        job = _jobs[job_id]
        try:
            def hook(d):
                if d['status'] == 'downloading':
                    p = d.get('_percent_str', '0').replace('%','')
                    job["progress"] = float(p) / 100 if p.replace('.','').isdigit() else 0
                    job["speed"] = d.get('_speed_str', '')
                    job["eta"] = d.get('_eta_str', '')
                    job["status"] = "Downloading..."

            # Quality Logic: Finds best video UP TO the requested height
            # 4K = 2160, 2K = 1440, etc.
            format_str = 'bestaudio/best' if is_audio else f'bestvideo[height<={quality}]+bestaudio/best'
            
            opts = {
                'outtmpl': os.path.join(os.path.expanduser("~"), "Downloads", '%(title)s.%(ext)s'),
                'progress_hooks': [hook],
                'format': format_str,
                'merge_output_format': 'mp4',
            }

            import yt_dlp
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                job["title"] = info.get('title', 'Video')

            job["status"] = "Completed"
            job["progress"] = 1
            job["done"] = True
        except Exception as e:
            job["status"] = "Error"
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
            time.sleep(0.5)
    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
