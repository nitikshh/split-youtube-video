from flask import Flask, render_template, request, send_file, url_for
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os
from celery import Celery

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

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

@celery.task
def split_video_task(video_path):
    try:
        video = VideoFileClip(video_path)
        duration = video.duration
        half_duration = duration / 2

        part1_path = os.path.join(DOWNLOAD_FOLDER, 'part1.mp4')
        part2_path = os.path.join(DOWNLOAD_FOLDER, 'part2.mp4')

        video.subclip(0, half_duration).write_videofile(part1_path, codec='libx264')
        video.subclip(half_duration, duration).write_videofile(part2_path, codec='libx264')

        return part1_path, part2_path
    except Exception as e:
        return str(e)

@app.route('/process', methods=['POST'])
def process():
    try:
        video_url = request.form['video_url']
        video_path = download_youtube_video(video_url)
        
        # Start asynchronous task for splitting video
        task = split_video_task.delay(video_path)

        return "Video processing started. Check back later for download links."
    except Exception as e:
        return str(e), 500

@app.route('/downloads/<filename>')
def downloaded_video(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename))

if __name__ == '__main__':
    app.run(debug=True)
