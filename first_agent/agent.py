import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt.tool_executor import ToolExecutor
from tools import get_weather_tool, retrieve_documents_tool
from typing import TypedDict, List, Union, Literal

load_dotenv()

# ================== 1. 初始化 LLM 和工具 ==================
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-12-01-preview",
)

tools = [get_weather_tool, retrieve_documents_tool]
tool_executor = ToolExecutor(tools)

# ================== 2. 定义 State ==================
class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage, ToolMessage]]

# ================== 3. 定义节点函数 ==================
def call_model(state: AgentState):
    """Agent 节点：调用 LLM（绑定工具）"""
    llm_with_tools = llm.bind_tools(tools)
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def call_tool(state: AgentState):
    """Tools 节点：执行工具调用"""
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls
    results = []
    for tool_call in tool_calls:
        result = tool_executor.invoke(tool_call)
        results.append(result)
    return {"messages": results}

def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """条件边：判断是否需要继续调用工具"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    else:
        return "end"

# ================== 4. 构建 LangGraph ==================
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)
workflow.add_edge("tools", "agent")
graph = workflow.compile()

# ================== 5. 辅助函数：转换消息格式 ==================
def convert_messages_to_langchain(messages_list):
    """将 st.session_state.messages 格式转换为 LangChain 消息对象列表"""
    result = []
    for msg in messages_list:
        if msg["role"] == "user":
            result.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            result.append(AIMessage(content=msg["content"]))
        # ToolMessage 在历史中不会出现，忽略
    return result

def extract_last_assistant_content(result_state):
    """从图执行结果中提取最后一个 AI 消息的内容"""
    for msg in reversed(result_state["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "（未获得有效回答）"

# ================== 6. Streamlit 界面 ==================
st.set_page_config(page_title="AI Agent", page_icon="🤖", layout="centered")
st.title("🤖 AI Agent")
st.caption("我可以帮你查天气、回答你私人文档中的问题。")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 将对话历史转换为 LangChain 消息格式
    langchain_messages = convert_messages_to_langchain(st.session_state.messages)

    # 调用 LangGraph
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                result = graph.invoke({"messages": langchain_messages})
                answer = extract_last_assistant_content(result)
            except Exception as e:
                answer = f"处理出错：{str(e)}"
        st.markdown(answer)

    # 添加助手回复到历史
    st.session_state.messages.append({"role": "assistant", "content": answer})