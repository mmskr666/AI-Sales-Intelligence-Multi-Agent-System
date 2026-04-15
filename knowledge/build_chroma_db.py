from knowledge.rag_tools import load_text, cleaned_text, spilt_text
from knowledge.vector_store import build_vector


def build_chroma_db():
    docs = load_text("./industry.txt")
    cleaned = cleaned_text(docs)
    split_docs = spilt_text(cleaned)
    build_vector(split_docs)

    print("✅ 向量数据库构建完成")

if __name__ == "__main__":
    build_chroma_db()