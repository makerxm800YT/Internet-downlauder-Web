# ▶ YouTube Downloader

<p align="center">
  <img src="favicon.svg" width="80" alt="Logo"/>
</p>

<p align="center">
  <strong>Free · Unlimited · With Sound · Accounts · History · Web UI</strong>
</p>

<p align="center">
  A beautiful, modern local web app for downloading YouTube videos at maximum quality.<br/>
  Runs in your browser. No subscription. No limits. No ads. Forever free.
</p>

---

## ✨ Features

| | Feature | Details |
|---|---|---|
| 🔐 | **Accounts** | Sign in with Email/Password or Google — your history saved per account |
| ⬇ | **Max Quality** | Up to 4K — video and audio merged automatically |
| 🔊 | **Sound Always Works** | FFmpeg is bundled — zero manual setup |
| 🎵 | **Audio Only** | MP3 / M4A at 320kbps |
| 📋 | **Playlists** | Download full playlists in one click |
| 🕘 | **History** | Every download logged — re-download with one click |
| ⭐ | **Rate Us** | Built-in star rating system |
| 🔄 | **Self-Updating** | Update yt-dlp from inside the app |
| 🌐 | **Beautiful Web UI** | Runs in your browser — looks like a real app |

---

## 🚀 Quick Start

### Windows (2 steps)

1. Install Python → **[python.org/downloads](https://python.org/downloads)**  
   ⚠️ Check **"Add Python to PATH"** during install
2. Double-click **`START - Click Here.bat`**

The app installs everything and opens in your browser automatically. ✅

### Mac / Linux

```bash
pip install flask yt-dlp static-ffmpeg
python app.py
```
Then open **http://localhost:5000**

---

## 📁 Files

```
📦 youtube-downloader/
 ┣ 📄 app.py                  ← Flask backend (handles downloading)
 ┣ 📄 index.html              ← Web UI (opens in your browser)
 ┣ 🖼 favicon.svg             ← App icon
 ┣ 📄 START - Click Here.bat  ← Windows launcher
 ┗ 📄 README.md
```

---

## 🔒 Privacy

Everything is **100% local** — accounts, history, downloads.  
Nothing is sent to any server. Your data stays on your machine in `~/.ytdl_app/`.

---

## 🛠 Built With

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube engine
- [Flask](https://flask.palletsprojects.com/) — Local web server
- [static-ffmpeg](https://pypi.org/project/static-ffmpeg/) — Bundled audio merging
- Vanilla HTML/CSS/JS — No frameworks, no bloat

---

## 📄 License

MIT — free to use, fork, and share.
