const express = require('express');
const ytdl = require('@distube/ytdl-core');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.static('.')); // Serves your index.html

app.get('/download', async (req, res) => {
    const videoURL = req.query.url;
    const quality = req.query.quality || 'highest';

    if (!ytdl.validateURL(videoURL)) {
        return res.status(400).send('Invalid YouTube URL');
    }

    try {
        const info = await ytdl.getInfo(videoURL);
        const title = info.videoDetails.title.replace(/[^\x00-\x7F]/g, ""); // Clean title

        res.header('Content-Disposition', `attachment; filename="${title}.mp4"`);
        
        // This streams the video directly to the user
        ytdl(videoURL, {
            quality: quality,
            format: 'mp4'
        }).pipe(res);

    } catch (err) {
        console.error(err);
        res.status(500).send('Internal Server Error');
    }
});

const PORT = 3000;
app.listen(PORT, () => console.log(`Server running at http://localhost:${PORT}`));
