import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_MODEL = "gpt-4o-mini"

    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
    PRICES_DIR = os.path.join(DATA_DIR, "prices")

    EMBEDDING_MODEL = "intfloat/multilingual-e5-large"

    STORE_SEARCH_RADIUS_KM = 5
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"