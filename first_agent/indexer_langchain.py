# first_agent/indexer_langchain.py
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter # 正确的导入方式[reference:10]
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from document_loader_langchain import load_document
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = "knowledge" # 文件夹路径 = 待索引文件夹名称
CHROMA_DB_PATH = "./chroma_db"  # 向量库将保存在这里
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"

def build_knowledge_base():
    # 1. 加载所有文档，统一返回 Document  all_docs = [Document1, Document2, ...]
    all_docs = []
    for filename in os.listdir(KNOWLEDGE_DIR):
        file_path = os.path.join(KNOWLEDGE_DIR, filename) #文件路径
        docs = load_document(file_path) 
        all_docs.extend(docs)   #把 docs 列表里的每个元素拆开，依次追加到 all_docs 中，结果是扁平的 [doc1, doc2, doc3, ...]。
                                #extend 把多个小列表“摊平”成一个大列表，方便统一处理。
    if not all_docs:
        print("未找到任何文档。")
        return

    # 2. 切分文档块 (chunking)  chunks = [Chunk1, Chunk2, ...]   # 每个 Chunk 是更小的 Document
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        add_start_index=True, #在元数据中记录块在原文档中的起始位置[reference:11]
    )
    chunks = text_splitter.split_documents(all_docs)
    print(f"文档已切分为 {len(chunks)} 个块")

    # 3. 创建嵌入模型和向量库。   HuggingFaceEmbeddings是一个很好的适配器，这是嵌入模型的接口
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # 4. 存入 Chroma 向量库  只需定义，自动执行
    vector_store = Chroma.from_documents(
        documents=chunks,  #将文本块
        embedding=embeddings, #用嵌入模型
        persist_directory=CHROMA_DB_PATH,  # 存到 指定持久化目录 否则只会在内存，程序结束了就会丢掉
        collection_name="my_knowledge_langchain" #并命名为my_knowledge_langchain
    )
    
    print(f"成功索引 {len(chunks)} 个文档块到 {CHROMA_DB_PATH}")

if __name__ == "__main__":
    build_knowledge_base()