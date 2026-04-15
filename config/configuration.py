import os

API_KEY = os.environ.get('DEEPSEEK_API_KEY')
BASE_URL = "https://api.deepseek.com"
chat_model = "deepseek-build"
G_NEWS_KEY = "c3fa71397f2c1cf70679edbd2b6e3353"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_DB_PATH = "./data/chroma_db"
CROSS_ENCODER_MODEL_NAME = "BAAI/bge-reranker-base"
