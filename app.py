import os
from flask import Flask, request, render_template, send_from_directory
from moviepy.editor import VideoFileClip

app = Flask(__name__)

def split_video(video_path):
    video = VideoFileClip(video_path)
    duration = video.duration
    half_duration = duration / 2

    part1_path = os.path.join('downloads', 'part1.mp4')
    part2_path = os.path.join('downloads', 'part2.mp4')

    video.subclip(0, half_duration).write_videofile(part1_path, codec='libx264', temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
    video.subclip(half_duration, duration).write_videofile(part2_path, codec='libx264', temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')

    return part1_path, part2_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        video = request.files['video']
        video_path = os.path.join('uploads', video.filename)
        video.save(video_path)

        part1_path, part2_path = split_video(video_path)

        return render_template('index.html', part1_path=part1_path, part2_path=part2_path)
    except Exception as e:
        return str(e), 500

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory('downloads', filename)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('downloads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
