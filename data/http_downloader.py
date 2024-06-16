import requests
from .video_loader import VideoDownloader

class HTTPVideoDownloader(VideoDownloader):
    def download_video(self, url, output_path):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
