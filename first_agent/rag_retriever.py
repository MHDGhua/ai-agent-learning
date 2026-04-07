import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 与索引时相同的配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_PATH = os.path.join(BASE_DIR, "../chroma_db")
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"

_vectorstore = None
_retriever = None

def get_retriever(top_k: int = 2):
    global _vectorstore, _retriever
    if _retriever is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        _vectorstore = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=embeddings,
            collection_name="my_knowledge"
        )
        _retriever = _vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )
    return _retriever

def retrieve_documents(query: str, top_k: int = 2) -> str:
    retriever = get_retriever(top_k)
    docs = retriever.invoke(query)
    if not docs:
        return "未找到相关信息。"
    return "\n\n".join([doc.page_content for doc in docs])