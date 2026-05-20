from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.rag.embeddings import EmbeddingModel
import uuid

class VectorStore:
    def __init__(self, collection_name: str = "foundations"):
        # Прямые значения (хардкод)
        url = "https://6147f21b-c372-4319-9945-285e453a502d.eu-west-1-0.aws.cloud.qdrant.io"
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6MDdkMTU0ODktYzdjMy00YmE1LTg0YzUtZDU1YTYzMGU4MDk5In0.x6PUPEQqpap0OQM460jZP5_ZGieI9-jfUEeTV3_v9PY"
        
        print(f"🔗 Подключение к Qdrant Cloud: {url}")
        
        self.client = QdrantClient(url=url, api_key=api_key)
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
                print(f"✅ Коллекция {self.collection_name} создана")
            else:
                print(f"✅ Коллекция {self.collection_name} уже существует")
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")

    def _add_sample_documents(self):
        documents = [
            {"text": "СП 22.13330.2016: Свайные фундаменты на торфах", "source": "СП 22.13330.2016"},
            {"text": "ГОСТ 25100-2020: Классификация грунтов", "source": "ГОСТ 25100-2020"},
            {"text": "УШП для пучинистых грунтов", "source": "Техническая рекомендация"},
        ]
        points = []
        for i, doc in enumerate(documents):
            vector = self.embedding_model.encode([doc["text"]])[0]
            points.append(PointStruct(
                id=i,
                vector=vector.tolist(),
                payload={"text": doc["text"], "source": doc["source"]}
            ))
        self.client.upsert(collection_name=self.collection_name, points=points)
        print(f"✅ Добавлено {len(points)} документов")

    def search(self, query: str, limit: int = 5) -> list:
        vector = self.embedding_model.encode_query(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector.tolist(),
            limit=limit
        )
        return [{"text": hit.payload["text"], "score": hit.score, "source": hit.payload.get("source", "")} for hit in results]