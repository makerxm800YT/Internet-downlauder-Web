<div align="center">

<img src="favicon.svg" width="90" alt="YTDL Logo"/>

# YTDL — YouTube Downloader

**Download Anything. Zero Limits.**

[![Free](https://img.shields.io/badge/Price-Free-brightgreen?style=flat-square)](.)
[![No Ads](https://img.shields.io/badge/Ads-None-red?style=flat-square)](.)
[![Private](https://img.shields.io/badge/Data-100%25%20Local-blue?style=flat-square)](.)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?style=flat-square)](https://python.org)

*A beautiful, fast, local web app for downloading YouTube videos at maximum quality.*
*Runs in your browser. No subscriptions. No limits. No ads. Forever free.*

</div>

---

## ✨ Features

| | What it does |
|---|---|
| ⬇ | **Max Quality Downloads** — up to 4K, video + audio merged automatically |
| 🔊 | **Always with Sound** — FFmpeg is bundled, zero setup needed |
| 🎵 | **Audio Only** — MP3 / M4A at 320kbps |
| 📋 | **Full Playlist Support** — download entire playlists in one click |
| 🖼 | **Thumbnails in History** — see the video preview for every past download |
| 🔐 | **Accounts** — Email or Google sign-in, settings saved per user |
| 🕘 | **Download History** — re-download any past video in one click |
| 🎛 | **Custom Dropdowns** — animated rounded UI, not boring system selects |
| ✨ | **Smooth Animations** — logo launch, hero text, page transitions |
| 🌐 | **Network Sharing** — anyone on your WiFi can use it from their device |
| 🔄 | **Self-Updating** — update yt-dlp from inside the app |
| ⭐ | **Rate Us** — built-in star rating |

---

## 🚀 Quick Start

### Windows — 2 steps

1. Install Python → **[python.org/downloads](https://python.org/downloads)**
   > ⚠️ Check **"Add Python to PATH"** during install — required!

2. Double-click **`START - Click Here.bat`**

Browser opens at `http://localhost:5000` automatically. ✅

### Mac / Linux

```bash
pip install flask yt-dlp static-ffmpeg
python app.py
```

Then open **[http://localhost:5000](http://localhost:5000)**

---

## 📁 Project Files

```
📦 ytdl/
 ┣ 📄 app.py                   ← Python backend (Flask server + downloader)
 ┣ 📄 index.html               ← Full web UI — everything in one file
 ┣ 🖼  favicon.svg              ← Premium app icon
 ┣ 📄 START - Click Here.bat   ← Windows one-click launcher
 ┗ 📄 README.md
```

> **Note:** `app.js` is **not needed** — delete it if you have it. All JavaScript is inside `index.html`.

---

## 🌐 Use on Your Local Network

When you start the app, the terminal shows two URLs:

```
▸ Local    http://localhost:5000       ← you on this PC
▸ Network  http://192.168.x.x:5000    ← anyone on your WiFi
```

Share the **Network URL** with friends on the same WiFi — they can download from their phone or laptop, no install needed.

---

## 🔒 100% Private

- All accounts, history, and preferences stored in `~/.ytdl_app/` on **your machine only**
- Nothing is uploaded or sent to any external server
- No telemetry, no tracking, no ads — ever

---

## 🛠 Built With

| Tool | Purpose |
|---|---|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube downloading engine |
| [Flask](https://flask.palletsprojects.com/) | Local web server |
| [static-ffmpeg](https://pypi.org/project/static-ffmpeg/) | Bundled audio+video merging |
| Vanilla HTML/CSS/JS | UI — no frameworks, no bloat |

---

## 📄 License

MIT — free to use, modify, and share.
