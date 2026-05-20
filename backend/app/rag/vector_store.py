from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.rag.embeddings import EmbeddingModel
from app.config import Config
import uuid
import os


class VectorStore:
    def __init__(self, collection_name: str = "foundations"):
        # Подключение к облачному Qdrant
        url = Config.QDRANT_URL
        api_key = Config.QDRANT_API_KEY
        
        print(f"Подключение к Qdrant: URL={url}, API_KEY={api_key[:20] if api_key else 'None'}...")
        
        if api_key and url != "http://localhost:6333":
            self.client = QdrantClient(
                url=url,
                api_key=api_key
            )
        else:
            # Локальное подключение (для разработки)
            self.client = QdrantClient(host="localhost", port=6333)
        
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
                print(f"Коллекция {self.collection_name} создана")
            else:
                print(f"Коллекция {self.collection_name} уже существует")
        except Exception as e:
            print(f"Ошибка инициализации коллекции: {e}")

    def _add_sample_documents(self):
        documents = [
            {"text": "СП 22.13330.2016 Основания зданий и сооружений. Свайные фундаменты рекомендуются при слабых грунтах: торф, болото, плывуны.", "source": "СП 22.13330.2016"},
            {"text": "ГОСТ 25100-2020 Грунты. Классификация. Суглинки и глины требуют заглубления ниже глубины промерзания.", "source": "ГОСТ 25100-2020"},
            {"text": "УШП (утеплённая шведская плита) рекомендуется для пучинистых грунтов и домов с высокими нагрузками.", "source": "Техническая рекомендация"},
            {"text": "Ленточные фундаменты подходят для песчаных и скальных грунтов с небольшой нагрузкой.", "source": "СП 50.101.2004"},
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
            })
        return results