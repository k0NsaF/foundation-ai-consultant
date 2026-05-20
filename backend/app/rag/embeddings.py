class EmbeddingModel:
    def __init__(self):
        self.dimension = 768
    
    def encode(self, texts: list) -> list:
        return [[0.0] * self.dimension for _ in texts]
    
    def encode_query(self, query: str) -> list:
        return [0.0] * self.dimension