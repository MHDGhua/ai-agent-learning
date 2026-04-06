import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# 1. 初始化 LLM
llm = AzureChatOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    azure_deployment=deployment,
    api_version="2024-12-01-preview",
)

# 2. 定义辅助函数（日志、后处理）
def log_input(x: dict) -> dict:
    print(f"[用户问题]: {x.get('question')}")
    return x

def add_footer(text: str) -> str:
    return text + "\n\n--- 回答结束 ---"

# 3. 构建提示词模板（支持天气和通用问题）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手。对于天气问题，请用自然语言直接回答；对于其他问题，请提供准确、有帮助的信息。不要输出JSON。"),
    ("human", "{question}")
])


# 更简单的链：直接传递字典给 prompt
# 因为 prompt 需要 {"question": ...}，我们可以用 RunnablePassthrough 来传递
# 但为了清晰，我们直接用 lambda 包装
def prepare_input(x: dict) -> dict:
    return {"question": x["question"]}

chain = (
    RunnableLambda(log_input)
    | RunnableLambda(prepare_input)
    | prompt
    | llm
    | StrOutputParser()
    | RunnableLambda(add_footer)
)

# 5. 测试
questions = [
    "北京天气怎么样？",
    "什么是 LangChain？",
    "你好"
]

for q in questions:
    print("\n" + "="*50)
    result = chain.invoke({"question": q})
    print(result)