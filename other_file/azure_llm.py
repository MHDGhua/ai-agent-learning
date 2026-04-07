import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# 创建 LangChain 的 AzureChatOpenAI 实例
_llm = AzureChatOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    azure_deployment=DEPLOYMENT_NAME,
    api_version="2024-12-01-preview",
    # 注意：o4-mini 不支持 temperature，所以不设置
    # max_tokens 也不设置，让模型使用默认值
)

def call_llm(prompt: str) -> str:
    """与原始接口兼容的 LangChain 调用"""
    if not all([ENDPOINT, API_KEY, DEPLOYMENT_NAME]):
        return "错误：Azure OpenAI 配置不完整，请检查 .env 文件。"
    try:
        # 将 prompt 作为 HumanMessage 发送
        response = _llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"LLM 调用失败：{str(e)}"