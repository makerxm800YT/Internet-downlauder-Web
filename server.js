const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.static('.'));

app.get('/download', (req, res) => {
    const { url, quality, format, ext } = req.query;

    if (!url) return res.status(400).send('URL required');

    // Step 1: Get Video Title
    const getTitle = spawn('yt-dlp', ['--get-title', url]);
    let videoTitle = "StreamVault_Download";

    getTitle.stdout.on('data', (data) => {
        videoTitle = data.toString().trim().replace(/[/\\?%*:|"<>]/g, '-');
    });

    getTitle.on('close', () => {
        res.header('Content-Disposition', `attachment; filename="${videoTitle}.${ext || 'mp4'}"`);

        // Step 2: The Pro Downloader Logic
        let formatStr = `bestvideo[height<=${quality}]+bestaudio/best`;
        if (format === 'audio') formatStr = 'bestaudio/best';

        const ytdlp = spawn('yt-dlp', [
            '-f', formatStr,
            '--merge-output-format', ext || 'mp4',
            '--no-playlist',
            '-o', '-', 
            url
        ]);

        ytdlp.stdout.pipe(res);
        ytdlp.stderr.on('data', (data) => console.log(`[Engine]: ${data}`));
    });
});

app.listen(3000, () => console.log(`🚀 Desktop Engine live at http://localhost:3000`));
