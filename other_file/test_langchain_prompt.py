import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# 创建 LLM 实例（与昨天一致，不设置 temperature 和 max_tokens）
llm = AzureChatOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    azure_deployment=deployment,
    api_version="2024-12-01-preview",
)

# 构建提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能天气助手。当用户询问天气时，请用自然语言直接回答，不要输出JSON格式，不要调用任何工具。"),
    ("human", "{question}")
])

# 创建 LCEL 链：prompt → llm → output_parser
chain = prompt | llm | StrOutputParser()

# 测试
question = "北京天气怎么样？"
response = chain.invoke({"question": question})
print("回答：")
print(response)