from langchain_community.embeddings import HuggingFaceEmbeddings
from config.configuration import EMBEDDING_MODEL_NAME


def get_embedding():
    embedding = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )
    return embedding