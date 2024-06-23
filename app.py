from flask import Flask, request, jsonify, send_from_directory, render_template
from pytube import YouTube
from moviepy.editor import VideoFileClip, concatenate_videoclips
import random
import os

app = Flask(__name__)

def download_youtube_video(url, download_path="downloads"):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    output_path = stream.download(output_path=download_path)
    return output_path

def extract_clips(video_path, clip_duration=10, num_clips=3, target_width=1080):
    clip_paths = []
    video = VideoFileClip(video_path)

    video_duration = video.duration
    clip_duration = min(clip_duration, video_duration)

    start_times = random.sample(range(0, int(video_duration - clip_duration)), num_clips)

    for i, start_time in enumerate(start_times):
        end_time = start_time + clip_duration
        clip = video.subclip(start_time, end_time)

        # Calculate target height based on aspect ratio to maintain proportions
        target_height = int(target_width * clip.size[1] / clip.size[0])

        # Resize the clip maintaining aspect ratio
        clip_resized = clip.resize((target_width, target_height))

        # Save the resized clip
        clip_name = f"clip_{i+1}.mp4"
        output_clip_path = os.path.join("clips", clip_name)
        clip_resized.write_videofile(output_clip_path, codec='libx264', audio_codec='aac')

        clip_paths.append(output_clip_path)

    video.close()
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
    if not os.path.exists('clips'):
        os.makedirs('clips')
    app.run(debug=True)
