import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 与索引时相同的配置
CHROMA_DB_PATH = "../chroma_db"
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"

# 全局单例：向量存储和检索器
_vectorstore = None
_retriever = None

def get_retriever(top_k: int = 2):
    global _vectorstore, _retriever
    if _retriever is None:
         # 初始化嵌入模型
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
         # 加载已有的 Chroma 向量库
        _vectorstore = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=embeddings,
            collection_name="my_knowledge"
        )
        # 创建检索器
        _retriever = _vectorstore.as_retriever(  #as_retriever：将 Chroma 向量库转换为 LangChain 的 Retriever 对象。检索器提供统一的 invoke(query) 接口。
            search_type="similarity",  # 也可用 "mmr"
            search_kwargs={"k": top_k}
        )
    return _retriever

def retrieve_documents(query: str, top_k: int = 2) -> str:
    """与原始接口兼容的检索函数"""
    retriever = get_retriever(top_k)
    docs = retriever.invoke(query)
    if not docs:
        return "未找到相关信息。"
    # 将多个文档内容拼接为字符串
    return "\n\n".join([doc.page_content for doc in docs])

# 测试
if __name__ == "__main__":
    print(retrieve_documents("我的项目计划书第一段内容"))