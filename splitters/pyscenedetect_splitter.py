import os
import cv2
from scenedetect import SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.backends.opencv import VideoStreamCv2

class PySceneDetectSplitter:
    def split_video(self, video_path, output_segments_dir, video_id=None):
        video_stream = VideoStreamCv2(video_path)
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector())
        scene_manager.detect_scenes(video=video_stream)
        scene_list = scene_manager.get_scene_list()

        if not scene_list:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            scenes = [(0, duration)]
            cap.release()
        else:
            scenes = [(scene[0].get_seconds(), scene[1].get_seconds()) for scene in scene_list]

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        scene_paths = []

        for idx, (start_time, end_time) in enumerate(scenes):
            start_frame = int(start_time * fps)
            end_frame = int(end_time * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            output_filename = os.path.join(output_segments_dir, f'{video_id}_scene_{idx + 1}.mp4')
            scene_paths.append(output_filename)
            out = cv2.VideoWriter(output_filename, fourcc, fps, (
                int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            ))

            for frame_num in range(start_frame, end_frame):
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)

            out.release()

        cap.release()

        return scene_paths