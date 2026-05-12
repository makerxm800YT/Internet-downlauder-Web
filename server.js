const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.static('.'));

// Ensure a local downloads folder exists
const downloadDir = path.join(__dirname, 'temp_downloads');
if (!fs.existsSync(downloadDir)) fs.mkdirSync(downloadDir);

app.get('/download', (req, res) => {
    const { url, quality, format, ext } = req.query;
    if (!url) return res.status(400).send('URL required');

    console.log(`🚀 Starting stable download for: ${url}`);

    // Generate a unique filename to avoid collisions
    const fileId = Date.now();
    const tempFile = path.join(downloadDir, `dl_${fileId}.${ext || 'mp4'}`);

    let args = [
        '--ffmpeg-location', './ffmpeg.exe',
        '--no-playlist',
        '-o', tempFile
    ];

    if (format === 'audio') {
        args.push('-x', '--audio-format', 'mp3', '--audio-quality', '0');
    } else {
        args.push('-f', `bestvideo[height<=${quality}]+bestaudio/best`, '--merge-output-format', ext || 'mp4');
    }

    args.push(url);

    const ytdlp = spawn('./yt-dlp.exe', args);

    ytdlp.on('close', (code) => {
        if (code === 0) {
            // Once finished, send the actual completed file with sound
            res.download(tempFile, (err) => {
                if (!err) {
                    // Clean up: delete temp file after user gets it
                    setTimeout(() => fs.unlinkSync(tempFile), 60000); 
                }
            });
        } else {
            res.status(500).send('Engine Error: Check if FFmpeg.exe and yt-dlp.exe are in the folder.');
        }
    });

    ytdlp.stderr.on('data', (data) => console.log(`[LOG]: ${data}`));
});

app.listen(3000, () => console.log(`🚀 StreamVault Desktop: http://localhost:3000`));
