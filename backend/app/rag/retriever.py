from typing import List, Dict
from app.rag.vector_store import VectorStore

print("=== ЗАГРУЗКА retriever.py ===")

class RAGRetriever:
    def __init__(self):
        print("RAGRetriever.__init__ вызван")
        self.vector_store = VectorStore()
        print("RAGRetriever инициализирован")

    def build_search_query(self, user_input: str, enriched_params: Dict) -> str:
        parts = []
        if enriched_params.get("soil"):
            parts.append(f"грунт {enriched_params['soil']}")
        if enriched_params.get("material"):
            parts.append(f"дом из {enriched_params['material']}")
        parts.append(user_input)
        return " ".join(parts)

    def retrieve(self, user_input: str, enriched_params: Dict, top_k: int = 5) -> List[Dict]:
        print("RAGRetriever.retrieve вызван")
        query = self.build_search_query(user_input, enriched_params)
        return self.vector_store.search(query, limit=top_k)