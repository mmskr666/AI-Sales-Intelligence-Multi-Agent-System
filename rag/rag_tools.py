import json

from langchain_core.prompts import ChatPromptTemplate
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi
from config.configuration import CROSS_ENCODER_MODEL_NAME
from knowledge.rag_tools import load_text, clean_txt, cleaned_text, spilt_text
from prompt.multi_prompt import multi_prompt
from prompt.rewrite_prompt import rewrite_prompt
from tools.llm_factory import create_llm

prompt_rewrite = ChatPromptTemplate.from_messages([
    ("system",rewrite_prompt),
    ("human","用户输入：{text}")
])
chain_rewrite = prompt_rewrite | create_llm()
def rewrite(text:str):
   result = chain_rewrite.invoke({"text":text})
   return result.content


prompt_multi = ChatPromptTemplate.from_messages([
    ("system",multi_prompt),
    ("human","用户输入：{text}")
])
chain_multi = prompt_multi | create_llm()
def multi_query(text:str):
    response = chain_multi.invoke({"text":text})
    return json.loads(response.content)

model = CrossEncoder(CROSS_ENCODER_MODEL_NAME)

def rerank_cross_encoder(query,docs,top_k=3):
    rank = []
    if not docs:
        return rank
    #crossEncoder标准数据接收格式[[问题,文档]]
    paris = [[query,doc.page_content] for doc in docs]
    #排序完的分数列表[0.7,0.8]
    scores = model.predict(paris)
    #组装
    rank = list(zip(scores,docs))

    rank.sort(key=lambda x:x[0],reverse=True)
    return [doc for _,doc in rank[:top_k]]

def hybrid_search(query, retriever, bm25,corpus,docs, k=5):
    # 🔹1. 向量检索
    vector_docs = retriever.invoke(query)

    # 🔹2. BM25检索（修复 numpy 类型报错）
    tokenized_query = list(query)
    scores = bm25.get_scores(tokenized_query)

    # ✅ 修复：把 numpy 数组转成普通 Python 列表（解决报错）
    scores = [float(s) for s in scores]

    # 取TopK BM25
    top_bm25_idx = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:k]

    bm25_docs = [docs[i] for i in top_bm25_idx]

    # 🔥3. 合并 + 去重（保持顺序）
    all_docs = vector_docs + bm25_docs
    unique_docs = []
    seen = set()

    for doc in all_docs:
        content = doc.page_content.strip()
        if content not in seen:
            seen.add(content)
            unique_docs.append(doc)

    # 4. 最多返回 k 个结果
    return unique_docs[:k]

def build_bm25():
    import os
    from langchain_community.document_loaders import TextLoader
    from rank_bm25 import BM25Okapi

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    file_path = os.path.join(project_root, "knowledge", "industry.txt")

    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()

    cleaned = cleaned_text(docs)
    split_docs = spilt_text(cleaned)

    corpus = [doc.page_content for doc in split_docs]
    tokenized_corpus = [list(text) for text in corpus]

    bm25 = BM25Okapi(tokenized_corpus)

    return bm25, corpus, split_docs   # ✅ 多返回一个 split_docs