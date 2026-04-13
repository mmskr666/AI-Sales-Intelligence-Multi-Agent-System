from konwledge.vector_store import load_vector


def get_retriever(k=3):
    db = load_vector()
    return db.as_retriever(search_type="mmr",kwargs={"K":k})