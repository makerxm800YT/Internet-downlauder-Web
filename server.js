const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.static('.'));

app.get('/download', (res, req) => {
    const videoURL = req.query.url;
    const quality = req.query.quality || '1080';

    if (!videoURL) return res.status(400).send('URL is required');

    // Clean filename logic
    const filename = `video_${Date.now()}.mp4`;

    res.header('Content-Disposition', `attachment; filename="${filename}"`);

    // The UNSTOPPABLE Engine: yt-dlp
    // It selects the best video up to the requested height + best audio
    const ytdlp = spawn('yt-dlp', [
        '-f', `bestvideo[height<=${quality}]+bestaudio/best`,
        '--merge-output-format', 'mp4',
        '-o', '-', // Stream to stdout (Standard Output)
        videoURL
    ]);

    ytdlp.stdout.pipe(res);

    ytdlp.stderr.on('data', (data) => {
        console.log(`[Log]: ${data}`);
    });

    ytdlp.on('close', (code) => {
        if (code !== 0) console.error(`Engine exited with code ${code}`);
    });
});

const PORT = 3000;
app.listen(PORT, () => console.log(`🚀 Unlimited Engine running at http://localhost:${PORT}`));
