# IDLR — Internet Downloader

A self-hosted media downloader with a clean web interface. Paste a link, IDLR detects the platform automatically, and grabs the video or audio you want — no ads, no redirects, no third-party upload wait times.

![IDLR banner](docs/screenshots/banner.png)

---

## ✨ Features

- **1000+ supported sites** via `yt-dlp`, plus dedicated audio handling for Spotify tracks/playlists via `spotdl`
- **Live URL detection** — paste a link and the UI instantly recognizes the platform and shows the right options, no need to press "check" first
- **Animated dropdowns** for format/quality selection
- **Slide-in settings panel** — download location, default quality, audio-only mode, and more, without leaving the page
- **Thumbnail preview** — see the video thumbnail (including HLS streams) before you commit to downloading
- **Bulk history management** — every past download is logged, searchable, and can be bulk-selected for re-download or deletion
- **Runs entirely on your own machine** — nothing leaves your network except the request to the source site

### Supported platforms

| Platform | Video | Audio |
|---|---|---|
| YouTube | ✅ | ✅ |
| Spotify | — | ✅ (via spotdl) |
| SoundCloud | — | ✅ |
| TikTok | ✅ | ✅ |
| 1000+ others (via yt-dlp) | ✅ | ✅ |

---

## 📸 Screenshots

> Replace these with real captures from your instance — drop images into `docs/screenshots/` and update the paths below.

| Home / URL detection | Settings panel | Download history |
|---|---|---|
| ![home](docs/screenshots/home.png) | ![settings](docs/screenshots/settings.png) | ![history](docs/screenshots/history.png) |

---

## 🧰 Prerequisites

- Python 3.10+
- `pip`
- `ffmpeg` installed and on your system `PATH` (required for audio extraction/merging)
- A modern browser (Chrome, Firefox, Edge)

---

## 🚀 Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/<your-username>/idlr.git
   cd idlr
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   This installs Flask, `yt-dlp`, `spotdl`, and any other packages the app needs.

4. **Install ffmpeg** (if not already installed)
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt install ffmpeg

   # Windows
   winget install ffmpeg
   ```

5. **Run the app**
   ```bash
   python app.py
   ```

6. **Open it in your browser**
   ```
   http://localhost:5000
   ```

---

## ⚙️ Configuration

Settings can be changed either from the in-app **Settings panel** or by editing the config file directly.

| Setting | Default | Description |
|---|---|---|
| Download folder | `./downloads` | Where finished files are saved |
| Default quality | `Best available` | Fallback quality if none is chosen per-download |
| Audio-only mode | `Off` | Strips video, saves audio only (mp3/m4a) |
| History limit | `Unlimited` | Max entries kept before auto-pruning |

> If your app reads these from a `.env` or `config.json` file, list the exact keys here so the README matches reality.

---

## 🖥️ Usage

1. Paste a URL into the input field — the platform badge appears automatically.
2. Pick a format/quality from the dropdown.
3. Hit **Download**.
4. Track progress and grab the finished file from the **History** panel.
5. Use the settings toggle (top corner) to adjust download location, quality defaults, or clear history in bulk.

---

## 🗂️ Project structure

```
idlr/
├── app.py                 # Flask entry point
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── templates/
│   └── index.html
├── downloads/              # Saved media (gitignored)
├── requirements.txt
└── README.md
```

> Update this tree to match your actual folder layout.

---

## 🐛 Known issues / troubleshooting

- **Thumbnails not loading for some links** — a handful of platforms serve thumbnails over HLS streams that aren't always parsed correctly; a fallback/manual-refresh option is in progress.
- **ffmpeg not found** — make sure it's installed and available on your PATH; restart your terminal after installing.
- **Spotify downloads slow or fail** — spotdl relies on matching tracks via YouTube; very obscure tracks may not find a match.

---

## 🤝 Contributing

This is a personal/self-hosted project, but pull requests and issue reports are welcome if you're running your own instance and find a bug.

## 📄 License

Add your license of choice here (MIT is a common default for personal projects like this).
