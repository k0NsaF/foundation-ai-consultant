from sentence_transformers import SentenceTransformer
import numpy as np
from app.config import Config


class EmbeddingModel:
    def __init__(self, model_name: str = Config.EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)
        self.dimension = 1024

    def encode(self, texts: list[str]) -> np.ndarray:
        prefixed_texts = [f"passage: {t}" for t in texts]
        return self.model.encode(prefixed_texts)

    def encode_query(self, query: str) -> np.ndarray:
        return self.model.encode(f"query: {query}")