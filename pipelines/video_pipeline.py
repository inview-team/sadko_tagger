import sys
import os
import csv
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.download_video import download_video
from captions.video_captions import Caption
from transcribe.whisper_transcriber import FasterWhisperTranscriber
from utils.process_text import clean_text, extract_terms
from translate.opus import OpusTranslate
from embeddings.minilm import MiniLMEmbed

classifier = Caption()
transcriber = FasterWhisperTranscriber(model_size='large-v3')
translator = OpusTranslate()
sentence_embedding = MiniLMEmbed()

def video_pipeline(video_id, video_url, description):
    output_dir = os.path.join('/home/lct/output', video_id)
    os.makedirs(output_dir, exist_ok=True)
    
    download_video(video_id, video_url, output_dir)
    
    segments_dir = os.path.join(output_dir, 'segments')

    actions = []
    content = []
    
    for video_file in os.listdir(segments_dir):
        video_path = os.path.join(segments_dir, video_file)
        if os.path.isfile(video_path):
            seg_actions, seg_content = classifier.caption_video(output_dir, video_path)
            actions.append(seg_actions)
            content.append(seg_content)    

    audio_path = os.path.join(output_dir, f'{video_id}.mp3')
    transcription_segments, info = transcriber.transcribe_audio(audio_path)
    transcriptions = [segment.text for segment in transcription_segments]

    flat_actions = [action for sublist in actions for action in sublist]
    flat_content = [item for sublist in content for item in sublist]
    description_terms = extract_terms(description)
    combined_list = flat_actions + flat_content + transcriptions + description_terms
    translated = translator.translate_batch(combined_list)
    cleaned_list = [clean_text(text, 'russian') for text in translated]
    vectors = sentence_embedding.embed_batch(cleaned_list)
    shutil.rmtree(output_dir)
    return vectors, cleaned_list

if __name__ == "__main__":
    with open('/home/lct/yappy.csv', encoding='utf-8') as csvfile:
        file_reader = csv.reader(csvfile)
        next(file_reader)
        n = 0
        for i in file_reader:
            url = i[0]
            description = i[1]
            video_pipeline(str(n), url)
            n+=1
            is_next = input("Next?:")
            if is_next != "y":
                break
