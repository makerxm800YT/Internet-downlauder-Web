<div align="center">

<img src="favicon.svg" width="100" alt="IDLR logo">

# IDLR — Internet Downloader

### Paste a link. Download. Done.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Server-black?style=flat-square&logo=flask)
![yt-dlp](https://img.shields.io/badge/yt--dlp-Video-red?style=flat-square)
![SpotDL](https://img.shields.io/badge/SpotDL-Spotify-1ed760?style=flat-square&logo=spotify&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

**YouTube · Spotify · TikTok · Instagram · SoundCloud · 1000+ sites**

No login. No cloud. Runs on your PC.

</div>

---

## What it does

1. Run the app on your computer  
2. Paste any video or music link  
3. Click **Download Now**  
4. File saves to your **Downloads** folder  
5. Shows up in the **History** tab  

Everything stays on your machine.

---

## Quick start

1. Install [Python 3.10+](https://www.python.org/downloads/) — tick **Add Python to PATH**
2. **Double-click `app.py`** in File Explorer (the Python file)
3. Your browser opens → **http://localhost:5000**

That's it. No terminal, no commands.

**To stop:** open Task Manager → end **Python** / **pythonw**

> First time only: Windows may ask how to open `.py` files — choose **Python**.

---

## What gets installed

| Package | Purpose |
|:--------|:--------|
| **Flask** | Runs the web app on your PC |
| **yt-dlp** | Downloads YouTube, TikTok, Instagram, etc. |
| **SpotDL** | Downloads Spotify as MP3 |
| **FFmpeg** *(auto)* | Audio/video conversion — needed for sound |

---

## Spotify (music)

Paste any Spotify link:

- Track, album, or playlist  
- Auto-switches to **Audio Only**  
- Saves as **MP3** (320 kbps) to Downloads  

---

## History tab

Every download is saved automatically. Open **History** to:

- See past downloads  
- Re-download a link  
- Delete items or clear all  

History is stored in `~/.idlr_app/history.json` on your PC.

---

## Profile (optional)

Click your name (top right) to set a display name or avatar.  
Saved locally in your browser — no account needed.

---

## Project files

```
├── app.py            # Double-click this to start
├── index.html        # Web UI
├── requirements.txt  # Dependencies
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
|:--------|:----|
| `python not recognized` | Reinstall Python with **Add to PATH** |
| App won't open | Keep the terminal window open while using IDLR |
| No sound in video | Run `pip install static-ffmpeg` |
| Spotify fails | Settings → **Update yt-dlp + spotdl** |
| YouTube error | Same — update yt-dlp in Settings |

---

## Disclaimer

For **personal use only**. Respect copyright and each site's terms of service.

---

<div align="center">

**IDLR — Internet Downloader** · MIT License · © 2026

</div>
