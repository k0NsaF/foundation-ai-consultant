from typing import List, Dict

class RAGRetriever:
    def __init__(self):
        self.vector_store = None
        print("RAGRetriever инициализирован (Qdrant отключён)")
    
    def retrieve(self, user_input: str, enriched_params: Dict, top_k: int = 5) -> List[Dict]:
        print("Поиск отключён, возвращаем пустой список")
        return []