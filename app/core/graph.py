import asyncio
import os
import sqlite3
from typing import Any, Dict

from langgraph.graph import StateGraph, END
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    from langgraph_checkpoint_sqlite import SqliteSaver

from app.core.nodes import node_audit_gatekeeper, node_execution_engine, node_intent_router
from app.core.state import AgentState


LERAP_SQLITE_PATH = os.getenv("LERAP_SQLITE_PATH", os.path.join("data", "lerap_memory.db"))


_graph = None


def _get_checkpointer():
    db_path_abs = os.path.abspath(LERAP_SQLITE_PATH)
    os.makedirs(os.path.dirname(db_path_abs), exist_ok=True)
    conn = sqlite3.connect(db_path_abs, check_same_thread=False)
    return SqliteSaver(conn)


def get_graph():
    global _graph
    if _graph is not None:
        return _graph

    workflow = StateGraph(AgentState)
    workflow.add_node("intent_router", node_intent_router)
    workflow.add_node("execution_engine", node_execution_engine)
    workflow.add_node("audit_gatekeeper", node_audit_gatekeeper)

    workflow.set_entry_point("intent_router")
    workflow.add_edge("intent_router", "execution_engine")
    workflow.add_edge("execution_engine", "audit_gatekeeper")
    workflow.add_edge("audit_gatekeeper", END)

    checkpointer = _get_checkpointer()
    _graph = workflow.compile(checkpointer=checkpointer)
    return _graph


async def run_task(task_id: str, user_input: str) -> AgentState:
    """
    运行单个任务：从初始 state 开始推进，最终落到 final_output/is_compliant/errors。
    """
    graph = get_graph()
    initial_state: AgentState = {
        "task_id": task_id,
        "user_input": user_input,
        "intent": "",
        "context_data": [],
        "draft_content": "",
        "is_compliant": False,
        "final_output": "",
        "errors": [],
    }

    # 使用 thread_id 作为 checkpointer 的可恢复键（与手册字段 task_id 对齐）
    config: Dict[str, Any] = {"configurable": {"thread_id": task_id}}

    result = await graph.ainvoke(initial_state, config=config)
    return result

