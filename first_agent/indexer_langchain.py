# first_agent/indexer_langchain.py
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = "knowledge"
CHROMA_DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"

# 定义文件扩展名到加载器的映射
LOADER_MAPPING = {
    ".txt": (TextLoader, {"encoding": "utf-8"}),
    ".pdf": (PyPDFLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    # 可以继续添加 .docx 等，需安装相应库
}

def load_documents_from_dir(directory: str):
    """遍历目录，根据扩展名选择加载器，返回 Document 列表"""
    all_docs = []
    for filename in os.listdir(directory):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in LOADER_MAPPING:
            print(f"跳过不支持的文件: {filename}")
            continue
        loader_cls, kwargs = LOADER_MAPPING[ext]
        file_path = os.path.join(directory, filename)
        try:
            loader = loader_cls(file_path, **kwargs)
            docs = loader.load()
            all_docs.extend(docs)
            print(f"已加载: {filename} -> {len(docs)} 个文档片段")
        except Exception as e:
            print(f"加载文件 {filename} 失败: {e}")
    return all_docs

def build_knowledge_base():
    # 1. 加载所有文档
    all_docs = load_documents_from_dir(KNOWLEDGE_DIR)
    if not all_docs:
        print("未找到任何文档。")
        return

    # 2. 切分文档块
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(all_docs)
    print(f"文档已切分为 {len(chunks)} 个块")

    # 3. 创建嵌入模型
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # 4. 存入 Chroma 向量库
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH,
        collection_name="my_knowledge_langchain"
    )
    print(f"成功索引 {len(chunks)} 个文档块到 {CHROMA_DB_PATH}")

if __name__ == "__main__":
    build_knowledge_base()