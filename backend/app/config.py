import os
from dotenv import load_dotenv
import os.path

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(env_path)

class Config:
    # GitHub Models
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_MODEL = "deepseek-chat"
    GITHUB_TEMPERATURE = 0.3
    GITHUB_MAX_TOKENS = 1500
    
    # Qdrant Cloud
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
    COLLECTION_NAME = "foundation_standards"
    
    # Embedding
    EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Open-Meteo (без ключа)
    OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Пути
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"