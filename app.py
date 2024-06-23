from flask import Flask, request, jsonify, send_from_directory, render_template
from pytube import YouTube
import random
import os
import ffmpeg

app = Flask(__name__)

def download_youtube_video(url, download_path="downloads"):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    output_path = stream.download(output_path=download_path)
    return output_path

def extract_clips(video_path, clip_duration=58, num_clips=10):
    clip_paths = []
    video_info = ffmpeg.probe(video_path)
    video_duration = float(video_info['format']['duration'])

    # Ensure clip duration doesn't exceed video duration
    clip_duration = min(clip_duration, video_duration)

    # Randomly select starting points for clips (avoid exceeding video duration)
    start_points = random.sample(range(0, int(video_duration - clip_duration)), num_clips)

    # Ensure the "clips" directory exists
    if not os.path.exists('clips'):
        os.makedirs('clips')

    for i, start_point in enumerate(start_points):
        clip_name = f"clip_{i+1}.mp4"
        output_clip_path = os.path.join("clips", clip_name)

        (
            ffmpeg
            .input(video_path, ss=start_point, t=clip_duration)
            .filter('scale', 1080, -1)
            .output(output_clip_path)
            .run(overwrite_output=True)
        )

        clip_paths.append(output_clip_path)
    
    return clip_paths

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    video_url = data['url']
    num_clips = int(data['num_clips'])
    duration = int(data['duration'])
    
    # Download the YouTube video
    video_path = download_youtube_video(video_url)
    
    # Extract clips
    clip_paths = extract_clips(video_path, clip_duration=duration, num_clips=num_clips)
    
    return jsonify(clip_paths)

@app.route('/clips/<path:filename>')
def download_file(filename):
    return send_from_directory('clips', filename)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
