import cv2
import numpy as np
import os
import easyocr
from faster_whisper import WhisperModel
from towhee import pipe

reader = easyocr.Reader(['en', 'ru']) 
model = WhisperModel("large-v3", device="cpu", compute_type="int8", download_root="../cache")


def extract_text_from_video(frames: list[str]) -> list[str]:
    result = []
    
    for frame in frames:
        image = cv2.imread(frame)
        if image is None:
            continue  

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        ret, bin = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)

        kernel = np.ones((3, 3), np.uint8)
        closing = cv2.morphologyEx(bin, cv2.MORPH_CLOSE, kernel)

        inv = cv2.bitwise_not(closing)
        cv2.imwrite(frame, inv)

        res = reader.readtext(frame, detail=0)
        if len(res) == 0:
            continue
        result.append(res)
    
    return result


class OCRTranscriber():
    def __init__(self):
        self.p_ocr = (
            pipe.input('frames')
            .map('frames', 'video_text', extract_text_from_video)
            .output('frames', 'video_text')
        )

    def ocr_frames(self, frames):
        segments = self.p_ocr(frames)
        return segments.get_dict()['video_text']


if __name__ == "__main__":
    path = ["/home/lct/output/1506092031_kartinki_s_nadpisiami_22.jpg"]
    ocr = OCRTranscriber()
    print(ocr.ocr_frames(path))
