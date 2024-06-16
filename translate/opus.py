from towhee import pipe, ops, DataCollection
import langid 

langid.set_languages(['ru', 'en'])

class OpusTranslate():
    def __init__(self):
        self.p_tr = (
            pipe.input('text')
            .map('text', 'translation', ops.machine_translation.opus_mt(model_name='opus-mt-en-ru'))
            .output('text', 'translation')
        )

    def detect_language(self, text):
        lang, _ = langid.classify(text)
        return lang

    def translate(self, text):
        lang = self.detect_language(text)
        if lang == 'ru':
            return text
        translation = self.p_tr(text)
        return translation.get_dict()['translation']

    def translate_batch(self, texts):
        translations = []
        for text in texts:
            lang = self.detect_language(text)
            if lang == 'ru':
                translations.append(text)  
            else:
                translation = self.p_tr(text)
                translations.append(translation.get_dict()['translation'])
        return translations

if __name__ == "__main__":
    text = ["bitch i am young thug", "no i am", "привет", "Dota 2"]
    opus = OpusTranslate()
    translation = opus.translate_batch(text)
    print(translation)
