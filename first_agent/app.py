# first_agent/app.py
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent
from langchain_tools import get_weather_tool, retrieve_documents_tool

load_dotenv()

# 初始化 LLM
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-12-01-preview",
    timeout=30,
)

# 创建 Agent（全局单例）
tools = [get_weather_tool, retrieve_documents_tool]
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个智能助手，可以查询天气和检索私有知识库。",
    debug=False,
)

# Streamlit 界面
st.set_page_config(page_title="AI Agent", page_icon="🤖", layout="centered")
st.title("🤖 AI Agent")
st.caption("我可以帮你查天气、回答你私人文档中的问题。")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # LangChain Agent 调用
                response = agent.invoke({
                    "messages": [{"role": "user", "content": prompt}]
                })
                answer = response["messages"][-1].content
            except Exception as e:
                answer = f"处理出错：{str(e)}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})