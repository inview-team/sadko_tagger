from towhee import pipe, ops, DataCollection
import numpy as np
from glob import glob
import os
from PIL import Image


def label(predicts, scores, topk=5):
    labels = {}
    for i in range(topk):
        labels[predicts[i]] = scores[i]
    return labels

def prepare_frames(video_frames, output_dir, num_frames=1):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    n = 0
    image_list = []
    for i, frame in enumerate(video_frames['frames']):
        if n == num_frames:
            break
        if isinstance(frame, np.ndarray):
            img = Image.fromarray(frame, mode=frame._mode)
            path = os.path.join(output_dir, f"frame_{i}.png")
            img.save(path)
            image_list.append(path)
            n += 1
        else:
            raise TypeError(f"Frame {i} is not a numpy array")

    return image_list

class Caption():
    def __init__(self, topk=5, device='cuda:0'):
        self.topk = topk
        self.device = device
        self.p_pr = (
            pipe.input('video_path')
            .map('video_path', 'frames', ops.video_decode.ffmpeg(sample_type='uniform_temporal_subsample', args={'num_samples': 32}))
            .output('frames')
        )
        self.p_act = (
            pipe.input('frames')
            .map('frames', ('predicts', 'scores', 'features'), ops.action_classification.pytorchvideo(model_name='x3d_m', skip_preprocess=True, topk=5))
            .output('predicts')
        )
        self.p_content = (
            pipe.input('path')
            .map('path', 'img', ops.image_decode.cv2_rgb())
            .map('img', 'predicts', ops.image_captioning.blip(model_name='blip_base'))
            .output('predicts')
        )

    def caption_video(self, output_dir, video_path):
        video_frames = self.p_pr(video_path)
        video_frames = video_frames.get_dict()
        actions = self.p_act(video_frames['frames']).get_dict()['predicts']
        content_frames = prepare_frames(video_frames=video_frames, output_dir=output_dir, num_frames=1)
        content = self.p_content.batch(content_frames)
        content_output = []
        for i in content:
            content_output.append(i.get_dict()['predicts'])
        return actions, content_output


if __name__ == "__main__":
    video_path = '/home/dilaks/lct/output/52cbde754a5e91923ff0b36934d4_scene_5.mp4'  # Replace with the actual video path
    classifier = Caption()

    actions, content = classifier.caption_video(video_path)
    #frames, actions, content = classifier.caption_video(video_path)
    #print(frames)
    #print("------------------")
    print(actions)
    #print("------------------")
    print(content)
