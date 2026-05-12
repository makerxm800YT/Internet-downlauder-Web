const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.static('.'));

// FIXED: (req, res) order corrected here
app.get('/download', async (req, res) => {
    const videoURL = req.query.url;
    const quality = req.query.quality || '1080';

    if (!videoURL) return res.status(400).send('URL is required');

    try {
        // Fetch the title first so the file name looks professional
        const getTitle = spawn('yt-dlp', ['--get-title', videoURL]);
        let videoTitle = "video";
        
        getTitle.stdout.on('data', (data) => {
            videoTitle = data.toString().trim().replace(/[/\\?%*:|"<>]/g, '-');
        });

        getTitle.on('close', () => {
            res.header('Content-Disposition', `attachment; filename="${videoTitle}.mp4"`);

            // Start the actual high-speed download
            const ytdlp = spawn('yt-dlp', [
                '-f', `bestvideo[height<={quality}]+bestaudio/best`,
                '--merge-output-format', 'mp4',
                '-o', '-', 
                videoURL
            ]);

            ytdlp.stdout.pipe(res);

            ytdlp.stderr.on('data', (data) => {
                console.log(`[Engine Log]: ${data}`);
            });
        });
    } catch (err) {
        console.error("Critical Engine Error:", err);
        res.status(500).send('Internal Server Error');
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`\n========================================`);
    console.log(`🚀 UNLIMITED ENGINE IS LIVE`);
    console.log(`🌐 http://localhost:${PORT}`);
    console.log(`========================================\n`);
});
