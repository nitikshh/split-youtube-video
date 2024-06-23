const express = require('express');
const multer = require('multer');
const ytdl = require('ytdl-core');
const path = require('path');
const fs = require('fs');

const app = express();
const upload = multer();

app.use(express.static('public'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.post('/process', upload.none(), async (req, res) => {
  try {
    const videoUrl = req.body.url;
    const videoId = ytdl.getURLVideoID(videoUrl);
    const videoPath = path.join(__dirname, 'public', 'videos', `${videoId}.mp4`);

    // Create videos directory if it doesn't exist
    if (!fs.existsSync(path.join(__dirname, 'public', 'videos'))) {
      fs.mkdirSync(path.join(__dirname, 'public', 'videos'), { recursive: true });
    }

    // Download the video
    const stream = ytdl(videoUrl, { filter: 'audioandvideo', format: 'mp4' });
    stream.pipe(fs.createWriteStream(videoPath));

    stream.on('end', () => {
      res.send({
        success: true,
        videoPath: `/videos/${videoId}.mp4`
      });
    });

    stream.on('error', (error) => {
      console.error('Error downloading video:', error);
      res.status(500).send({ success: false, error: 'Failed to download video' });
    });

  } catch (error) {
    console.error('Error processing request:', error);
    res.status(500).send({ success: false, error: 'An error occurred' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
