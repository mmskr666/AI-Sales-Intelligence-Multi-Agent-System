import os

API_KEY = os.environ.get('DEEPSEEK_API_KEY')
BASE_URL = "https://api.deepseek.com"
chat_model = "deepseek-chat"
NEWS_KEY = "e86497d7e5224f7ebe7a53b53ab49750"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_DB_PATH = "./data/chroma_db"
CROSS_ENCODER_MODEL_NAME = "BAAI/bge-reranker-base"