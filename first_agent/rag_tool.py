import chromadb
from chromadb.utils import embedding_functions
import os

# 获取当前脚本所在目录（first_agent）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录（上一级）
PROJECT_ROOT = os.path.dirname(BASE_DIR)
# 数据库路径统一放在项目根目录下
DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(
    name="my_knowledge",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name='all-MiniLM-L6-v2'
    )
)

# 全局初始化（确保路径正确，假设运行脚本时当前目录为项目根目录）
client = chromadb.PersistentClient(path="./chroma_db") #数据库
collection = client.get_collection(#集合
    name="my_knowledge",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name='all-MiniLM-L6-v2'
    )
)

def retrieve_documents(query: str, top_k: int = 2) -> str:
    """
    根据用户问题检索知识库，返回最相关的文档片段（合并为字符串）
    """
    try:
        results = collection.query(query_texts=[query], n_results=top_k)
        if results['documents'] and results['documents'][0]:
            return "\n\n".join(results['documents'][0])
        else:
            return "未找到相关信息"
    except Exception as e:
        return f"检索失败：{str(e)}"