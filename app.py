from flask import Flask, render_template, request, send_file, url_for
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os
import redis

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Redis client initialization
redis_host = 'localhost'  # Replace with your Redis server host
redis_port = 6379         # Replace with your Redis server port
redis_db = 0              # Replace with your Redis database number

redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

@app.route('/')
def index():
    return render_template('index.html', video1_url=None, video2_url=None)

def download_youtube_video(url):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    if not stream:
        raise ValueError("No suitable streams found for the video.")
    video_path = stream.download(output_path=DOWNLOAD_FOLDER)
    return video_path

def split_video(video_path):
    video = VideoFileClip(video_path)
    duration = video.duration
    half_duration = duration / 2

    part1_path = os.path.join(DOWNLOAD_FOLDER, 'part1.mp4')
    part2_path = os.path.join(DOWNLOAD_FOLDER, 'part2.mp4')

    video.subclip(0, half_duration).write_videofile(part1_path, codec='libx264')
    video.subclip(half_duration, duration).write_videofile(part2_path, codec='libx264')

    return part1_path, part2_path

@app.route('/process', methods=['POST'])
def process():
    try:
        video_url = request.form['video_url']
        video_path = download_youtube_video(video_url)
        part1_path, part2_path = split_video(video_path)

        # Example of storing file paths in Redis
        redis_client.set('part1_path', part1_path)
        redis_client.set('part2_path', part2_path)

        video1_url = url_for('downloaded_video', filename='part1.mp4')
        video2_url = url_for('downloaded_video', filename='part2.mp4')

        return render_template('index.html', video1_url=video1_url, video2_url=video2_url)
    except Exception as e:
        return str(e), 500

@app.route('/downloads/<filename>')
def downloaded_video(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename))

if __name__ == '__main__':
    app.run(debug=True)
