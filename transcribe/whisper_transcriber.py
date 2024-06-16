import os
from faster_whisper import WhisperModel
from pydub import AudioSegment

import sys
sys.path.append('/home/miniconda3/envs/torch-ws/bin/ffmpeg')

class FasterWhisperTranscriber():
    def __init__(self, model_size='large-v3'):
        self.model = WhisperModel(model_size)

    def transcribe_audio(self, audio_path):
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        return segments, info

if __name__ == "__main__":
    audio_path = "/home/lct/output/52cbde754a5e91923ff0b36934d4.mp3"
    transcriber = FasterWhisperTranscriber(model_size='large-v3')
    transcription_segments, info = transcriber.transcribe_audio(audio_path)
    for segment in transcription_segments:
        print(segment.text)
