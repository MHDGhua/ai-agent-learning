# first_agent/app.py
import streamlit as st
import sys
import os

# 确保能导入同级目录的 react_agent
sys.path.append(os.path.dirname(__file__))
from react_agent import react_agent

# 页面配置
st.set_page_config(
    page_title="我的 AI Agent",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 自定义 CSS 美化（可选）
st.markdown("""
<style>
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stButton > button {
        width: 100%;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e6f7ff;
        border-left: 5px solid #1890ff;
    }
    .assistant-message {
        background-color: #f6f6f6;
        border-left: 5px solid #52c41a;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 标题
st.title("🤖 我的 AI Agent")
st.caption("支持天气查询、私有知识库问答")

# 显示历史对话
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入框
if prompt := st.chat_input("输入你的问题..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用 Agent
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            answer = react_agent(prompt)
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.sidebar:
        st.header("ℹ️ 关于")
        st.write("这是一个基于 ReAct 模式的 AI Agent。")
        st.write("**可用工具：**")
        st.write("- 🌤️ 天气查询")
        st.write("- 📚 知识库检索")
        if st.button("清空对话"):
            st.session_state.messages = []
            st.rerun()
    with st.chat_message("user", avatar="🧑"):
        ...
    with st.chat_message("assistant", avatar="🤖"):
        ...