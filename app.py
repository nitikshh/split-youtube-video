from flask import Flask, render_template, request, send_file, url_for
from pytube import YouTube
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html', video_url=None)

def download_youtube_video(url):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    if not stream:
        raise ValueError("No suitable streams found for the video.")
    video_path = stream.download(output_path=DOWNLOAD_FOLDER)
    return video_path

@app.route('/process', methods=['POST'])
def process():
    try:
        video_url = request.form['video_url']
        video_path = download_youtube_video(video_url)
        video_filename = os.path.basename(video_path)
        video_url = url_for('downloaded_video', filename=video_filename)
        return render_template('index.html', video_url=video_url)
    except Exception as e:
        return str(e), 500

@app.route('/downloads/<filename>')
def downloaded_video(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename))

if __name__ == '__main__':
    app.run(debug=True)
