<div align="center">

<img src="favicon.svg" width="100" alt="IDLR logo">

# IDLR — Internet Downloader

### Download videos and music from the web. Simple, private, on your PC.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Server-black?style=flat-square&logo=flask)
![yt-dlp](https://img.shields.io/badge/yt--dlp-Video%20%26%20Audio-red?style=flat-square)
![SpotDL](https://img.shields.io/badge/SpotDL-Spotify%20Music-1ed760?style=flat-square&logo=spotify&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Audio%20Engine-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

**YouTube · Spotify · TikTok · Instagram · SoundCloud · 1000+ sites**

No cloud. No tracking. Runs on your computer.

<br>

[Quick Start](#-quick-start) · [Spotify](#-spotify-music-downloads) · [How to Use](#-how-to-use) · [Troubleshooting](#-troubleshooting)

</div>

---

<br>

## What is IDLR?

**IDLR** is a local web app you run on your PC. Open it in your browser, paste a link, and download.

| | |
|---|---|
| **Runs on** | Your computer only |
| **Needs internet?** | Yes — to fetch the link |
| **Saves files to** | Your `Downloads` folder |
| **Account data** | Stored locally in `~/.idlr_app/` |

---

## ✨ Features

| Feature | Details |
|:--------|:--------|
| 🌐 **1000+ sites** | YouTube, TikTok, Instagram, Twitter/X, SoundCloud, and more |
| 🎵 **Spotify** | Full tracks, albums, playlists — saved as MP3 (via SpotDL) |
| 🎬 **Video** | MP4, MKV, WEBM — up to 4K |
| 🔊 **Audio** | MP3, M4A, FLAC, OGG, WAV — up to 320 kbps |
| 📜 **History** | Re-download past links anytime |
| 👤 **Profile** | Name, avatar, settings — saved on your PC |
| 📱 **Wi-Fi sharing** | Open from phone/tablet on the same network |
| 🔄 **Updates** | One-click yt-dlp + SpotDL update in Settings |
| 🔒 **Private** | No servers, no analytics, no cookies |

---

## 📦 What you need

Install these **once** — `start.bat` installs them for you automatically.

| Package | What it does |
|:--------|:-------------|
| **[Python 3.10+](https://www.python.org/downloads/)** | Runs the app |
| **[Flask](https://flask.palletsprojects.com/)** | Powers the web interface |
| **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** | Downloads from YouTube, TikTok, Instagram, etc. |
| **[SpotDL](https://github.com/spotDL/spotify-downloader)** | Downloads Spotify music as audio files |
| **[FFmpeg](https://ffmpeg.org/)** *(via static-ffmpeg)* | Converts and merges audio/video — **required for sound** |

> **Audio note:** FFmpeg is included automatically (`static-ffmpeg`). Without it, video downloads may have no sound and Spotify/MP3 exports will fail.

---

## 🚀 Quick Start

### Windows — easiest way

1. Install [Python 3.10+](https://www.python.org/downloads/) — check **"Add Python to PATH"**
2. Double-click **`start.bat`**
3. Your browser opens → **http://localhost:5000**
4. Sign in or create an account
5. Paste a link → click **Download Now**

### Manual install

```bash
# 1. Clone or download this folder
cd Internet-downlauder-Web-main

# 2. Install all dependencies (Flask + audio + Spotify)
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Then open **http://localhost:5000** in your browser.

> **First run tip:** The app can also auto-install missing packages when you run `python app.py` — but using `pip install -r requirements.txt` first is more reliable.

---

## 🎵 Spotify music downloads

Spotify links are handled differently from YouTube — IDLR uses **SpotDL** to fetch and save audio.

### Supported Spotify links

```
https://open.spotify.com/track/...
https://open.spotify.com/album/...
https://open.spotify.com/playlist/...
```

### What you get

| Setting | Result |
|:--------|:-------|
| Format | **MP3** (default), M4A, FLAC, OGG |
| Quality | **320 kbps** |
| Save location | `Downloads` folder |

### How to download from Spotify

1. Copy a Spotify track, album, or playlist link
2. Paste it in IDLR
3. IDLR auto-detects Spotify and switches to **Audio Only**
4. Click **Download Now**
5. Wait for the green **Download complete** message

> SpotDL finds matching audio from public sources and converts it with FFmpeg. You need an active internet connection.

---

## 📖 How to use

### Download a video (YouTube, TikTok, etc.)

1. Run `start.bat` or `python app.py`
2. Paste the URL
3. Choose **Mode** → Video
4. Pick **Quality** (1080p, 4K, Best, etc.)
5. Pick **Format** → MP4
6. Click **⬇ Download Now**

### Download audio only

1. Paste the URL (or use a Spotify link)
2. Choose **Mode** → Audio Only
3. Pick **Bitrate** → 320 kbps
4. Pick **Format** → MP3
5. Click **⬇ Download Now**

### Use on your phone (same Wi-Fi)

1. Keep the app running on your PC
2. Go to **Settings** in IDLR
3. Copy the **Network** URL (e.g. `http://192.168.1.5:5000`)
4. Open that URL on your phone's browser

---

## 🗂 Project files

```
Internet-downlauder-Web-main/
├── app.py              # Flask server + download engine
├── index.html          # Web interface
├── requirements.txt    # Flask, yt-dlp, SpotDL, FFmpeg
├── start.bat           # One-click launcher (Windows)
├── favicon.svg         # App icon
├── LICENSE             # MIT
└── README.md           # This file
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|:--------|:----|
| `python is not recognized` | Reinstall Python and tick **Add to PATH** |
| `Cannot reach server` | Make sure `app.py` is running — don't close the terminal |
| **No sound** in video | FFmpeg missing — run `pip install static-ffmpeg` |
| **Spotify fails** | Run `pip install --upgrade spotdl` then use **Settings → Update yt-dlp + spotdl** |
| Download goes to wrong folder | In the app, click **Save Location** and set your path |
| YouTube error | Click **Settings → Update yt-dlp + spotdl** for the latest fix |
| Port already in use | Close other apps on port 5000, or restart your PC |

### Reinstall everything cleanly

```bash
pip install -r requirements.txt --upgrade
python app.py
```

---

## ⚖️ Disclaimer

**For personal use only.**

- Only download content you own, have rights to, or that is freely licensed
- Downloading copyrighted material without permission may violate platform terms and local law
- IDLR uses open-source tools: **yt-dlp**, **SpotDL**, and **FFmpeg** — each has its own license
- You are responsible for how you use this software

---

## 🛠 Built with

| Tool | Role |
|:-----|:-----|
| [Flask](https://flask.palletsprojects.com/) | Local web server |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Video & general downloads |
| [SpotDL](https://github.com/spotDL/spotify-downloader) | Spotify → MP3 |
| [FFmpeg](https://ffmpeg.org/) | Audio/video conversion |

---

<div align="center">

**IDLR — Internet Downloader**

*Fast · Private · Self-Hosted*

MIT License · © 2026

</div>
