# first_agent/api.py
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent
from tools import get_weather_tool, retrieve_documents_tool

# 加载 .env 文件（支持从项目根目录读取）
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 初始化 FastAPI  
# 自动被服务器调用
app = FastAPI(title="AI Agent API", description="异步调用你的智能助手")  

# 初始化 LLM（确保环境变量已设置）
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-12-01-preview",
)

tools = [get_weather_tool, retrieve_documents_tool]
#全局初始化agent
agent = create_agent(model=llm, tools=tools)

#定义Pydantic模型，后续调用
class Query(BaseModel):
    question: str

#装饰器是一个函数，它接收另一个函数作为参数，并返回一个新的函数（通常添加了额外功能）
#将函数写进路由表
@app.post("/chat")
async def chat(query: Query):  #query是形参，Query是参数类型提醒，告诉FastAPI 知道这是一个 Pydantic 模型
    """异步调用 Agent 回答用户问题"""
    result = await agent.ainvoke({"messages": [{"role": "user", "content": query.question}]})
    answer = result["messages"][-1].content
    return {"answer": answer}