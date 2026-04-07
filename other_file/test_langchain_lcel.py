import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

llm = AzureChatOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    azure_deployment=deployment,
    api_version="2024-12-01-preview",
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能天气助手。当用户询问天气时，请用自然语言直接回答。"),
    ("human", "{question}")
])

# 定义一个自定义函数，用于打印并返回输入
def log_input(x):
    print(f"[DEBUG] 用户问题: {x['question']}")
    return x   # 必须返回原字典，供后续节点使用

# 将函数包装为 RunnableLambda
log_node = RunnableLambda(log_input)

# 构建链：log_node → prompt → llm → parser
chain = log_node | prompt | llm | StrOutputParser()

# 测试
question = "北京天气怎么样？"
response = chain.invoke({"question": question})
print("\n最终回答:")
print(response)