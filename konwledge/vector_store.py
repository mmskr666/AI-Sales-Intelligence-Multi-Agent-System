from langchain_community.vectorstores import Chroma

from konwledge.embedding import get_embedding
from config.configuration import CHROMA_DB_PATH


def build_vector(docs):
    embedding = get_embedding()
    db = Chroma.from_documents(
        docs,
        embedding,
        persist_directory=CHROMA_DB_PATH
    )
    db.persist()


def load_vector():
    embedding = get_embedding()
    db = Chroma(
        embedding_function=embedding,
        persist_directory=CHROMA_DB_PATH
    )
    return db