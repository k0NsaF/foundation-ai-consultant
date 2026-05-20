import fitz
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.rag.vector_store import VectorStore
from pathlib import Path

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def process_pdf(file_path: str) -> list[dict]:
    doc = fitz.open(file_path)
    documents = []
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    
    chunks = chunk_text(full_text)
    for i, chunk in enumerate(chunks):
        documents.append({
            "text": chunk,
            "source": Path(file_path).name,
            "type": "snip",
            "metadata": {"chunk": i}
        })
    return documents

def main():
    vector_store = VectorStore()
    docs_dir = Path("data/raw")
    
    if not docs_dir.exists():
        print(f"Папка {docs_dir} не найдена. Создайте её и положите PDF файлы.")
        return
    
    pdf_files = list(docs_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"Нет PDF файлов в папке {docs_dir}")
        return
    
    for pdf_file in pdf_files:
        print(f"Обработка: {pdf_file.name}")
        documents = process_pdf(str(pdf_file))
        vector_store.add_documents(documents)
        print(f"Добавлено {len(documents)} чанков")

if __name__ == "__main__":
    main()