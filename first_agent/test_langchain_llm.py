import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

llm = AzureChatOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    azure_deployment=deployment,
    api_version="2024-12-01-preview",
    # temperature 参数移除
    max_tokens=500,
)

messages = [
    SystemMessage(content="你是一个智能助手，能够根据用户问题决定使用工具并回答。"),
    HumanMessage(content="北京天气怎么样？")
]

response = llm.invoke(messages)
print("LangChain 调用结果：")
print(response.content)