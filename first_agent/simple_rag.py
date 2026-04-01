import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions 

#指定路径-创建数据库  切片-索引嵌入em-导入向量数据库  问题-切片-索引嵌入em-召回-检索

# 1. 加载嵌入模型
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# 2. 创建Chroma客户端
client = chromadb.PersistentClient(path="./chroma_db")#创建本地向量数据库，路径为当前文件夹下./chroma_db，保存在磁盘PersistentClient
collection = client.get_or_create_collection( #创建或获取集合：如果有my_knowledge集合，则直接接获取，如果没有就创建新集合。
    name="my_knowledge", #集合的名称，理解成向量数据库中的一张表
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name='all-MiniLM-L6-v2') #定义嵌入函数：使用SentenceTransformer库的嵌入函数，指定使用的预训练模型。
)

# 3. 加载文档 切块 再存到列表
docs = [ ]
#列表 推导式：把“循环、条件判断、处理、收集”这四步压缩成一行，写起来更简洁，运行效率也略高，
file_paths = [ f"knowledge/{filename}"  #f"knowledge/{f}" 将文件夹名和.txt.文件名拼接。-----os.listdir("knowledge") 列出文件夹下所有.txt文件
              for filename in os.listdir("knowledge")
                 if filename.endswith(".txt") ]

for path in file_paths: #循环每次取一个文件路径，赋值给变量path
    #以只读模式打开当前文件路径path, with是文件操作后自动关闭
    with open(path, "r", encoding="utf-8") as filename:
        text = filename.read()#这个文件路径下的文本
    chunks = text.split("\n\n")#之所以得到一个列表，是因为Python字符串的split()方法总是返回一个列表。这个列表就是原本文档的切块列表
    
    for i, chunk in enumerate(chunks):  #enumerate 同时获取每个元素的索引和值。
        if chunk.strip():  #去掉前后空白行
            docs.append({"source": path, "text": chunk,  "chunk_id": i}) #作为字典添加到列表中

# 4. 插入向量数据库
ids = [ f"{doc['source']}_{doc['chunk_id']}"
        for doc in docs ]
texts = [ doc["text"] 
         for doc in docs ]
metadatas = [ {"source": doc["source"]} 
             for doc in docs ]
collection.add(
    documents=texts,
    metadatas=metadatas,
    ids=ids
)

# 5. 检索函数
def retrieve(query, top_k=2):
    #collection.query 该方法会自动将用户问题用同一个嵌入模型转换成向量，然后与库中所有向量计算相似度，返回前 top_k 个结果。
    results = collection.query(query_texts=[query], n_results=top_k)
    return results['documents'][0]  # 返回文本片段列表

# 测试
if __name__ == "__main__":
    q = "什么是 ReAct Agent？"
    print(retrieve(q))


