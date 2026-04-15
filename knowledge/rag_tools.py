import re
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader,PyPDFLoader

def clean_txt(text: str) -> str:
    # 1. 去掉首尾空格
    text = text.strip()
    # 2. 把换行、制表符 → 空格
    text = text.replace("\n", " ").replace("\t", " ")
    # 3. 多个连续空格 → 1个空格
    text = re.sub(r"\s+", " ", text)
    # 4. 去掉乱码、特殊符号（医疗文本只保留中文、英文、数字、常用符号）
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s%.,:;()（）。，、：；]", "", text)
    # 5. 再次去首尾
    return text.strip()

def load_text(file_path: str):
    loder = TextLoader(file_path,encoding="utf-8")
    return loder.load()

def cleaned_text(docs:list[Document]):
    cleaned_docs = []
    for doc in docs:
        text = clean_txt(doc.page_content)
        cleaned_docs.append(text)
    return cleaned_docs

def spilt_text(docs):
    recursive = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=30,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    return recursive.create_documents(docs)
