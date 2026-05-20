from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.rag.embeddings import EmbeddingModel
from app.config import Config
import uuid


class VectorStore:
    def __init__(self, collection_name: str = "foundations"):
        self.client = QdrantClient(
            host=Config.QDRANT_HOST, port=Config.QDRANT_PORT
        )
        self.collection_name = collection_name
        self.embedding_model = EmbeddingModel()
        self._init_collection()

    def _init_collection(self):
        try:
            collections = self.client.get_collections().collections
            names = [c.name for c in collections]

            if self.collection_name not in names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_model.dimension,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            print(f"Ошибка инициализации коллекции: {e}")

    def add_documents(self, documents: list[dict]):
        points = []
        for doc in documents:
            vector = self.embedding_model.encode([doc["text"]])[0]
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector.tolist(),
                payload={
                    "text": doc["text"],
                    "source": doc.get("source", ""),
                    "type": doc.get("type", ""),
                    "region": doc.get("region", ""),
                    "metadata": doc.get("metadata", {})
                }
            ))
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query: str, limit: int = 5) -> list[dict]:
        query_vector = self.embedding_model.encode_query(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=limit
        )
        return [
            {
                "text": hit.payload["text"],
                "score": hit.score,
                "source": hit.payload.get("source", ""),
                "type": hit.payload.get("type", "")
            }
            for hit in results
        ]