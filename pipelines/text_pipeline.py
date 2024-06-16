from utils.process_text import clean_text 
from translate.opus import OpusTranslate
from embeddings.minilm import MiniLMEmbed

translator = OpusTranslate()
sentence_embedding = MiniLMEmbed()

def text_pipeline(text):
    translated = translator.translate(text)
    cleaned_text = clean_text(translated, 'russian')
    vectors = sentence_embedding.embed(cleaned_text)
    print("vectors:", vectors)
    return vectors