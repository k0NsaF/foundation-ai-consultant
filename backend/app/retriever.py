from typing import List, Dict

class RAGRetriever:
    def __init__(self):
        print("RAGRetriever: RAG полностью отключён (заглушка)")
        self.vector_store = None

    def retrieve(self, user_input: str, enriched_params: Dict, top_k: int = 5) -> List[Dict]:
        print("RAG отключён, возвращаем пустой список")
        return []