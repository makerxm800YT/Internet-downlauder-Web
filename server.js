const express = require('express');
const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.static('.'));

const dlDir = path.join(__dirname, 'temp_downloads');
if (!fs.existsSync(dlDir)) fs.mkdirSync(dlDir);

app.get('/download', async (req, res) => {
    const { url, quality, format, ext } = req.query;
    if (!url) return res.status(400).send('URL required');

    try {
        // 1. Get the Real Title (FR Name)
        console.log("🔍 Fetching real video title...");
        const titleBuffer = execSync(`./yt-dlp.exe --get-title --no-playlist "${url}"`);
        const rawTitle = titleBuffer.toString().trim();
        // Clean the title so Windows/Mac can save it safely
        const cleanTitle = rawTitle.replace(/[/\\?%*:|"<>]/g, '-');
        
        const finalFilename = `${cleanTitle}.${ext || 'mp4'}`;
        const tempFilePath = path.join(dlDir, `dl_${Date.now()}.${ext || 'mp4'}`);

        console.log(`🚀 Downloading: ${cleanTitle}`);

        // 2. Start the download with Audio Merge
        const ytdl = spawn('./yt-dlp.exe', [
            '--ffmpeg-location', './ffmpeg.exe',
            '-f', format === 'audio' ? 'bestaudio/best' : `bestvideo[height<=${quality}]+bestaudio/best`,
            '--merge-output-format', ext || 'mp4',
            '--no-playlist',
            '-o', tempFilePath,
            url
        ]);

        ytdl.on('close', (code) => {
            if (code === 0) {
                // 3. Send the file with the REAL NAME
                res.download(tempFilePath, finalFilename, (err) => {
                    if (!err) {
                        // Clean up temp file after 2 minutes
                        setTimeout(() => {
                            if (fs.existsSync(tempFilePath)) fs.unlinkSync(tempFilePath);
                        }, 120000);
                    }
                });
            } else {
                res.status(500).send("Engine Error. Check if ffmpeg.exe exists.");
            }
        });

    } catch (error) {
        console.error("Name Detection Error:", error);
        res.status(500).send("Could not detect video name.");
    }
});

const PORT = 3000;
app.listen(PORT, () => console.log(`🚀 StreamVault Live at http://localhost:${PORT}`));
