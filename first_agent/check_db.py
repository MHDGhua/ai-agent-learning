import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(
    name="my_knowledge",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name='all-MiniLM-L6-v2'
    )
)

print(f"集合中的文档数量: {collection.count()}")
# 可选：打印前几个文档的 ID 和内容
results = collection.get(limit=5)
for i, (id, doc) in enumerate(zip(results['ids'], results['documents'])):
    print(f"ID: {id}, 内容预览: {doc[:100]}...")