from langchain.tools import tool
from weather_tool import get_weather
from rag_tool import retrieve_documents

#把普通的python函数包装成框架中tool对象，易于识别

@tool
def get_weather_tool(city: str) -> str:
    """查询指定城市的实时天气。"""
    return get_weather(city)

@tool
def retrieve_documents_tool(query: str) -> str:
    """从私有知识库中检索与 query 相关的文档片段。"""
    return retrieve_documents(query, top_k=2)


if __name__ == "__main__":
    print("天气工具测试：")
    print(get_weather_tool.invoke("北京"))
    
    print("\nRAG 工具测试：")
    print(retrieve_documents_tool.invoke("毕业论文 系统架构设计"))