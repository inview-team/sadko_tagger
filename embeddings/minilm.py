from towhee import pipe, ops

class MiniLMEmbed():
    def __init__(self):
        self.p_tr = (
            pipe.input('text')
            .map('text', 'vector', ops.sentence_embedding.sbert(model_name='all-MiniLM-L12-v2'))
            .output('vector')
        )

    def embed(self, text):
        vector = self.p_tr(text).get_dict()['vector']
        return vector

    def embed_batch(self, texts):
        embeddings = []
        embeds = self.p_tr.batch(texts)
        for e in embeds:
            embeddings.append(e.get_dict()['vector'])

        return embeddings