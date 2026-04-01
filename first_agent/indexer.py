import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

#索引函数

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DOCS_DIR = os.path.join(BASE_DIR, "knowledge")
DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

def build_knowledge_base(
    docs_path=DOCS_DIR,
    db_path=DB_PATH,
    collection_name="my_knowledge",
    chunk_size=500,
    chunk_overlap=50,
    model_name='all-MiniLM-L6-v2'
):
    """
    加载文档，切块，存入 Chroma 向量数据库。
    """
    # 1. 检查文档目录是否存在
    if not os.path.isdir(docs_path):
        print(f"错误：文档目录不存在：{docs_path}")
        return

    # 2. 加载所有 .txt 文件
    texts = []
    metadatas = []
    for filename in os.listdir(docs_path):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(docs_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # 切块
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", " ", ""]
        )
        chunks = splitter.split_text(content)
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({"source": filename, "chunk_id": i})

    if not texts:
        print("未找到任何文本片段，请检查文档内容或切块设置。")
        return

    # 3. 初始化 Chroma 客户端和集合
    client = chromadb.PersistentClient(path=db_path)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)

    # 如果集合已存在，先删除（可选：如果你希望增量更新，可以改用 get_or_create_collection）
    try:
        client.delete_collection(collection_name)
        print(f"已删除旧集合：{collection_name}")
    except ValueError:
        pass

    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )

    # 4. 生成唯一 ID
    ids = [f"{meta['source']}_{meta['chunk_id']}" for meta in metadatas]

    # 5. 添加文档
    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )

    print(f"索引完成！共添加 {len(texts)} 个片段。")
    print(f"数据库路径：{db_path}")
    print(f"集合名称：{collection_name}")

if __name__ == "__main__":
    build_knowledge_base()