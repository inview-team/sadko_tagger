from abc import ABC, abstractmethod

class VideoDownloader(ABC):
    @abstractmethod
    def download_video(self, url, output_path):
        pass