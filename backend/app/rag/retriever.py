from app.rag.vector_store import VectorStore
from typing import List, Dict


class RAGRetriever:
    def __init__(self):
        try:
            self.vector_store = VectorStore()
        except Exception as e:
            print(f"Ошибка инициализации VectorStore: {e}")
            self.vector_store = None

    def build_search_query(self, user_input: str, enriched_params: Dict) -> str:
        parts = []
        if enriched_params.get("soil"):
            parts.append(f"грунт {enriched_params['soil']}")
        if enriched_params.get("material"):
            parts.append(f"дом из {enriched_params['material']}")
        if enriched_params.get("floors"):
            parts.append(f"{enriched_params['floors']} этажа")
        parts.append(user_input)
        return " ".join(parts)

    def retrieve(self, user_input: str, enriched_params: Dict, top_k: int = 5) -> List[Dict]:
        if self.vector_store is None:
            return []
        query = self.build_search_query(user_input, enriched_params)
        return self.vector_store.search(query, limit=top_k)