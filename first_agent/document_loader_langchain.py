# first_agent/document_loader_langchain.py
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader

def load_document(file_path: str):
    """根据文件扩展名选择合适的 LangChain 加载器"""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    try:
        if ext == '.pdf':
            # PyPDFLoader 加载 PDF[reference:6]
            loader = PyPDFLoader(file_path)
            docs = loader.load()
        elif ext == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
            docs = loader.load()
        elif ext == '.md':
            loader = UnstructuredMarkdownLoader(file_path)
            docs = loader.load()
        # ... 可按需添加 .docx 等格式
        else:
            return []
        return docs
    except Exception as e:
        print(f"加载文件 {file_path} 失败: {e}")
        return []
    