import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.rag.embeddings import EmbeddingModel

print("=== ЗАГРУЗКА vector_store.py ===")
print(f"QDRANT_URL из окружения: {os.getenv('QDRANT_URL', 'НЕ УСТАНОВЛЕН')}")
print(f"QDRANT_API_KEY: {os.getenv('QDRANT_API_KEY', 'НЕ УСТАНОВЛЕН')[:30] if os.getenv('QDRANT_API_KEY') else 'НЕ УСТАНОВЛЕН'}...")


class VectorStore:
    def __init__(self, collection_name: str = "foundations"):
        # Читаем переменные окружения
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        
        print(f"\n=== ИНИЦИАЛИЗАЦИЯ VectorStore ===")
        print(f"Подключение к Qdrant: URL={qdrant_url}")
        print(f"API Key установлен: {'ДА' if qdrant_api_key else 'НЕТ'}")
        
        # Подключение к облачному Qdrant
        if qdrant_api_key and qdrant_url != "http://localhost:6333":
            try:
                self.client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key
                )
                print("✅ ПОДКЛЮЧЕНО К QDRANT CLOUD")
            except Exception as e:
                print(f"❌ Ошибка подключения к Qdrant Cloud: {e}")
                self.client = None
        else:
            # Локальное подключение (для разработки)
            try:
                self.client = QdrantClient(host="localhost", port=6333)
                print("⚠️ ПОДКЛЮЧЕНО К ЛОКАЛЬНОМУ QDRANT")
            except Exception as e:
                print(f"❌ Ошибка подключения к локальному Qdrant: {e}")
                self.client = None
        
        self.collection_name = collection_name
        self.embedding_model = EmbeddingModel()
        
        if self.client:
            self._init_collection()
        else:
            print("❌ Qdrant клиент не инициализирован, RAG не будет работать")

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
            print(f"❌ Ошибка инициализации коллекции: {e}")

    def _add_sample_documents(self):
        documents = [
            {"text": "СП 22.13330.2016: Свайные фундаменты на торфах и болотах", "source": "СП 22.13330.2016"},
            {"text": "ГОСТ 25100-2020: Классификация грунтов. Суглинки и глины требуют заглубления.", "source": "ГОСТ 25100-2020"},
            {"text": "УШП рекомендуется для пучинистых грунтов и высоких нагрузок", "source": "Техническая рекомендация"},
            {"text": "Ленточные фундаменты подходят для песчаных и скальных грунтов", "source": "СП 50.101.2004"},
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
        print(f"✅ Добавлено {len(points)} документов в коллекцию")

    def search(self, query: str, limit: int = 5) -> list[dict]:
        if not self.client:
            print("❌ Поиск невозможен: Qdrant клиент не инициализирован")
            return []
        
        try:
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
        except Exception as e:
            print(f"❌ Ошибка поиска в Qdrant: {e}")
            return []