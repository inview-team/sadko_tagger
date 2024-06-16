from towhee import pipe, ops

class BlipEmbedding():
    def __init__(self, model_name='blip_itm_large_coco', device='cpu'):
        self.model_name = model_name
        self.device = device

    def generate_video_embeddings(self, video_path):
        p = (
            pipe.input('video_path')
            .map('video_path', 'flame_gen', ops.video_decode.ffmpeg(sample_type='uniform_temporal_subsample', args={'num_samples': 12}))
            .map('flame_gen', 'flame_list', lambda x: [y for y in x])
            .map('flame_list', 'vec', ops.image_text_embedding.blip(model_name=self.model_name, modality='image'))
            .output('flame_list', 'vec')
        )
        
        result = p(video_path)
        return result.get_dict()
    
    def generate_video_captions(self, video_path):
        return "unimplemented"
    
    def generate_text_embedding(self, text):
        p = (
            pipe.input('text')
            .map('sentence', 'vec', ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='text', device=self.device))
        )
        
        result = p(text)
        return result.get_dict()

if __name__ == "__main__":
    video_path = '/home/lct/output/fhd_scene_1.mp4'
    embedding_generator = BlipEmbedding()
    embedding = embedding_generator.generate_video_embeddings(video_path)
    print(embedding)
    captions = embedding_generator.generate_video_captions(video_path)
    print(captions)
