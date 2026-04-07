import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, TodoListMiddleware
from langchain_tools import get_weather_tool, retrieve_documents_tool

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-12-01-preview",
)

# 1. 准备工具
tools = [get_weather_tool, retrieve_documents_tool]

# 2. 创建 Agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful AI assistant with access to weather and document retrieval tools.",
    # middleware=[
    #     SummarizationMiddleware(), # 自动总结对话历史
    #     TodoListMiddleware()       # 让 Agent 能够创建和管理任务清单
    # ],
    debug=True  # 开启调试模式，打印详细的执行日志
)

# 3. 执行 Agent
result = agent.invoke({"messages": [{"role": "user", "content": "我的私有文档中，有一个项目计划书，他的名字是什么"}]})
print(result["messages"][-1].content)