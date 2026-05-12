const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.static('.'));

app.get('/download', (req, res) => {
    const { url, quality, format, ext } = req.query;
    if (!url) return res.status(400).send('URL required');

    const getTitle = spawn('yt-dlp', ['--get-title', url]);
    let videoTitle = "StreamVault_Download";

    getTitle.stdout.on('data', (data) => {
        videoTitle = data.toString().trim().replace(/[/\\?%*:|"<>]/g, '-');
    });

    getTitle.on('close', () => {
        res.header('Content-Disposition', `attachment; filename="${videoTitle}.${ext || 'mp4'}"`);

        // PRO LOGIC: If audio only, use -x. If video, merge with ffmpeg.
        let args = [];
        if (format === 'audio') {
            args = ['-x', '--audio-format', 'mp3', '--audio-quality', '0', '-o', '-', url];
        } else {
            // This line forces the best video + best audio to merge into your chosen extension
            args = [
                '-f', `bestvideo[height<={quality}]+bestaudio/best`,
                '--merge-output-format', ext || 'mp4',
                '--ffmpeg-location', './ffmpeg.exe', // Tells the app to look in your folder
                '-o', '-', 
                url
            ];
        }

        const ytdlp = spawn('yt-dlp', args);
        ytdlp.stdout.pipe(res);
        
        ytdlp.stderr.on('data', (data) => {
            const log = data.toString();
            if (log.includes('ffmpeg not found')) {
                console.log("⚠️ FFmpeg missing! Audio will not work.");
            }
            console.log(`[Engine]: ${log}`);
        });
    });
});

app.listen(3000, () => console.log(`🚀 Desktop Engine live at http://localhost:3000`));
