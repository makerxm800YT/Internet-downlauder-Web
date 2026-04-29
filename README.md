# ▶ YouTube Downloader

> Free · Unlimited · With Sound · Accounts · History · Settings

A clean, dark-themed desktop YouTube downloader built with Python.  
Download any video at max quality — with full audio — for free, forever.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔐 Accounts | Sign in with Email or Google — your history is saved per account |
| ⬇ Max Quality | Downloads up to 4K — video and audio merged automatically |
| 🔊 Sound Always Works | FFmpeg is bundled — no manual setup needed |
| 🎵 Audio Only | Extract MP3 / M4A at 320kbps |
| 📋 Playlist Support | Download full playlists in one click |
| 🕘 History | Every download saved — re-download with one click |
| ⚙ Settings | Change save folder, update yt-dlp from inside the app |
| 🔄 Self-Updating | Click "Update yt-dlp" to stay current with YouTube changes |

---

## 🚀 How to Run

### Windows (easiest)
1. Install Python → [python.org/downloads](https://python.org/downloads)  
   ⚠️ Check **"Add Python to PATH"** during install
2. Download this repo as ZIP → Extract it
3. Double-click **`START - Click Here.bat`**  
   It installs everything and opens the app automatically ✅

### Mac / Linux
```bash
pip install yt-dlp static-ffmpeg
python ytdownloader.py
```

---

## 📦 Requirements

- Python 3.8+
- `yt-dlp` (auto-installed)
- `static-ffmpeg` (auto-installed — handles sound merging)

No other installs needed.

---

## 📁 Files

```
📦 ytdownloader/
 ┣ 📄 ytdownloader.py        ← Main app
 ┣ 📄 START - Click Here.bat ← Windows launcher (double-click this)
 ┗ 📄 README.md
```

Your account data and history are saved to `~/.ytdl_app/` on your computer.  
Nothing is sent online — fully local and private.

---

## 📸 Screenshots

| Login | Download | History |
|---|---|---|
| Email or Google sign-in | Paste URL, pick quality, download | All your past downloads |

---

## 🛠 Built With

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube downloading engine
- [static-ffmpeg](https://pypi.org/project/static-ffmpeg/) — Bundled FFmpeg for audio merging
- Python `tkinter` — GUI

---

## 📄 License

MIT — free to use, modify, and share.
