import sys
import os
from moviepy.editor import VideoFileClip

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.http_downloader import HTTPVideoDownloader
from splitters.pyscenedetect_splitter import PySceneDetectSplitter

def download_video(video_id, video_url, output_dir):
    video_path = os.path.join(output_dir, f'{video_id}.mp4')
    
    segments_dir = os.path.join(output_dir, 'segments')
    os.makedirs(segments_dir, exist_ok=True)
    
    downloader = HTTPVideoDownloader()
    downloader.download_video(video_url, video_path)
    
    splitter = PySceneDetectSplitter()
    splitter.split_video(video_path, segments_dir, video_id)

    video = VideoFileClip(video_path)
    audio_path = os.path.join(output_dir, f"{video_id}.mp3")
    video.audio.write_audiofile(audio_path)

if __name__ == "__main__":
    video_url = 'https://cdn-st.rutubelist.ru/media/9b/17/52cbde754a5e91923ff0b36934d4/fhd.mp4'
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    download_video("52cbde754a5e91923ff0b36934d4", video_url, output_dir)

