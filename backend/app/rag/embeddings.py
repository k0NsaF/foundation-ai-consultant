from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer("intfloat/multilingual-e5-large")
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def encode(self, texts: list) -> list:
        return self.model.encode(texts)
    
    def encode_query(self, query: str) -> list:
        return self.model.encode(query)