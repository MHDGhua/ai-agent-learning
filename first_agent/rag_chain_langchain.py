# first_agent/rag_chain_langchain.py
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
COLLECTION_NAME = "my_knowledge_langchain"

def get_rag_chain():
    # 1. 加载已有的向量库
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    
    # 2. 创建检索器 (Retriever)
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}  # 返回最相关的 3 个文档块
    )
    
    # 3. 定义 RAG 提示词模板
    prompt_template = """你是一个专业的助手，请基于以下内容回答用户的问题。
    
    内容：
    {context}
    
    问题：{question}
    
    回答："""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    # 4. 初始化 LLM
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_version="2024-12-01-preview",
        temperature=0,  # o4-mini 不支持，可以不传或注释
    )
    
    # 5. 构建 RetrievalQA 链
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # 将检索到的所有内容“填充”到提示词中
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True  # 返回引用的文档，方便溯源
    )
    
    return qa_chain

# 使用示例
if __name__ == "__main__":
    chain = get_rag_chain()
    result = chain.invoke({"query": "什么是 ReAct Agent?"})
    print(f"答案: {result['result']}")
    print(f"参考来源: {result['source_documents']}")