import os
import chromadb
from chromadb.utils import embedding_functions
from rag_tool import retrieve_documents  # 如果你已经封装了检索函数

def main():
    # 1. 测试查询
    queries = [
        "什么是 norm？"
    ]
    
    for q in queries:
        print(f"\n查询: {q}")
        print("-" * 50)
        # 调用检索函数（返回字符串）
        result = retrieve_documents(q, top_k=2)
        print(result)
        print()

if __name__ == "__main__":
    main()