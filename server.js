const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const app = express();

app.use(express.static('.'));

const dlDir = path.join(__dirname, 'downloads');
if (!fs.existsSync(dlDir)) fs.mkdirSync(dlDir);

app.get('/download', (req, res) => {
    const { url, quality, ext } = req.query;
    const finalFile = path.join(dlDir, `file_${Date.now()}.${ext}`);

    // This command FORCES yt-dlp to use the ffmpeg.exe we just downloaded
    const ytdl = spawn('./yt-dlp.exe', [
        '--ffmpeg-location', './ffmpeg.exe',
        '-f', `bestvideo[height<=${quality}]+bestaudio/best`,
        '--merge-output-format', ext,
        '-o', finalFile,
        url
    ]);

    ytdl.on('close', (code) => {
        if (code === 0) {
            res.download(finalFile, () => {
                // Delete temp file after 1 minute to save space
                setTimeout(() => { if(fs.existsSync(finalFile)) fs.unlinkSync(finalFile); }, 60000);
            });
        } else {
            res.status(500).send("Audio Merge Failed. Run the .bat again!");
        }
    });
});

app.listen(3000, () => console.log("Engine Online at http://localhost:3000"));
