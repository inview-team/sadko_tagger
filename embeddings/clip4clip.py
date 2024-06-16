from towhee import pipe, ops, DataCollection

class Clip4ClipEmbedding():
    def __init__(self, model_name='clip_vit_b32', device='cuda:0'):
        self.model_name = model_name
        self.device = device

    def generate_video_embeddings(self, video_path):
        p = (
            pipe.input('video_path')
            .map('video_path', 'frames', ops.video_decode.ffmpeg(sample_type='uniform_temporal_subsample', args={'num_samples': 12}))
            .map('frames', 'vec', ops.video_text_embedding.clip4clip(model_name=self.model_name, modality='video', device=self.device))
            .output('frames', 'vec')
        )
        
        result = p(video_path)
        return result.get_dict()
    
    def generate_video_captions(self, video_path):
        return "unimplemented"
    
    def generate_text_embeddings(self, text):
        p = (
            pipe.input('text')
            .map('text', 'vec', ops.video_text_embedding.clip4clip(model_name='clip_vit_b32', modality='text', device=self.device))
            .output('text', 'vec')
        )
        
        result = p(text)
        return result.get_dict()

if __name__ == "__main__":
    video_path = '/home/dilaks/lct/output/fhd_scene_1.mp4'
    embedding_generator = Clip4ClipEmbedding()
    embedding = embedding_generator.generate_video_embeddings(video_path)
    print(embedding)
