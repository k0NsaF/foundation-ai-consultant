from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.rag.embeddings import EmbeddingModel
from app.config import Config
import uuid


class VectorStore:
    def __init__(self, collection_name: str = "foundations"):
        # Подключение к облачному Qdrant
        self.client = QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY
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
                self._add_sample_documents()
        except Exception as e:
            print(f"Ошибка инициализации коллекции: {e}")

    def _add_sample_documents(self):
        """Добавляем примеры нормативных документов"""
        documents = [
            {"text": "СП 22.13330.2016 Основания зданий и сооружений. Свайные фундаменты рекомендуются при слабых грунтах: торф, болото, плывуны.", "source": "СП 22.13330.2016"},
            {"text": "ГОСТ 25100-2020 Грунты. Классификация. Суглинки и глины требуют заглубления ниже глубины промерзания.", "source": "ГОСТ 25100-2020"},
            {"text": "УШП (утеплённая шведская плита) рекомендуется для пучинистых грунтов и домов с высокими нагрузками.", "source": "Техническая рекомендация"},
            {"text": "Ленточные фундаменты подходят для песчаных и скальных грунтов с небольшой нагрузкой.", "source": "СП 50.101.2004"},
            {"text": "Мелкозаглубленная лента подходит для лёгких домов на песчаных грунтах.", "source": "СП 50.101.2004"},
        ]
        
        points = []
        for i, doc in enumerate(documents):
            vector = self.embedding_model.encode([doc["text"]])[0]
            points.append(PointStruct(
                id=i,
                vector=vector.tolist(),
                payload={
                    "text": doc["text"],
                    "source": doc.get("source", ""),
                }
            ))
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Добавлено {len(points)} документов в коллекцию")

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
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=limit
        )
        results = []
        for hit in search_result:
            results.append({
                "text": hit.payload["text"],
                "score": hit.score,
                "source": hit.payload.get("source", ""),
                "type": hit.payload.get("type", "")
            })
        return results