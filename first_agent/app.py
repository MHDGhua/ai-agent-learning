import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent
from tools import get_weather_tool, retrieve_documents_tool
import time

load_dotenv()

# 初始化 LLM（o4-mini 不支持 temperature，不传该参数）
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-12-01-preview",
    # 注意：没有 temperature 参数
)

tools = [get_weather_tool, retrieve_documents_tool]
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个智能助手，可以查询天气和检索私有知识库。",
    debug=False,
)

st.set_page_config(page_title="AI Agent", page_icon="🤖", layout="centered")
st.title("🤖 AI Agent")
st.caption("我可以帮你查天气、回答你私人文档中的问题。")

if "messages" not in st.session_state:
    st.session_state.messages = []

MAX_MESSAGES = 10
def truncate_messages():
    if len(st.session_state.messages) > MAX_MESSAGES:
        st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    truncate_messages()
    with st.chat_message("user"):
        st.markdown(prompt)

    # with st.chat_message("assistant"):
    #     response_placeholder = st.empty()
    #     full_response = ""
    #     # 流式调用
    #     for chunk in agent.stream({"messages": st.session_state.messages}):
    #         if "messages" in chunk:
    #             last_msg = chunk["messages"][-1]
    #             # 只处理 AIMessage 且内容非空，忽略 ToolMessage 等
    #             if hasattr(last_msg, "content") and last_msg.content and not hasattr(last_msg, "tool_calls"):
    #                 full_response += last_msg.content
    #                 response_placeholder.markdown(full_response + "▌")
    #     response_placeholder.markdown(full_response)

    # with st.chat_message("assistant"):
    #     with st.spinner("思考中..."):
    #         response = agent.invoke({"messages": st.session_state.messages})
    #         answer = response["messages"][-1].content
    #     st.markdown(answer)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        # 调用 Agent（非流式，一次性获取完整答案）
        response = agent.invoke({"messages": st.session_state.messages})
        answer = response["messages"][-1].content
        
        # 模拟逐字输出（打字机效果）
        full_response = ""
        for char in answer:
            full_response += char
            response_placeholder.markdown(full_response + "▌")
            time.sleep(0.02)   # 控制速度，可调整为 0.01 或 0.03
        response_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    truncate_messages()