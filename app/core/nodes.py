from __future__ import annotations

from typing import Any, Dict, List

from app.core.state import AgentState
from app.services import llm_client, rag_retriever


def _append_errors(state: AgentState, new_errors: List[str]) -> List[str]:
    prev = list(state.get("errors", []))
    for err in new_errors:
        text = str(err)
        if text not in prev:
            prev.append(text)
    return prev


def _fallback_intent(user_input: str) -> str:
    text = (user_input or "").lower()
    if any(k in text for k in ["申请书", "答辩书", "证据清单", "代理词", "文书", "生成"]):
        return "draft"
    if any(k in text for k in ["审计", "审查", "核查", "对抗"]):
        return "audit"
    return "query"


async def node_intent_router(state: AgentState) -> Dict[str, Any]:
    """
    路由中枢：根据 user_input 得到 intent。
    """
    user_input = state["user_input"]
    try:
        intent = await llm_client.classify_intent(user_input)
        return {"intent": intent}
    except Exception as e:
        return {
            "intent": _fallback_intent(user_input),
            "errors": _append_errors(state, [f"意图路由失败: {type(e).__name__}"]),
        }


async def node_execution_engine(state: AgentState) -> Dict[str, Any]:
    """
    业务执行中台：RAG 召回 context_data + 生成 draft_content。
    """
    user_input = state["user_input"]
    intent = state["intent"]

    try:
        context_data = rag_retriever.retrieve_context(user_input, top_k=3)
        draft_content = await llm_client.generate_draft(user_input, intent, context_data)
        return {"context_data": context_data, "draft_content": draft_content}
    except Exception as e:
        # 发生异常时降级：context_data 为空，draft_content 给拦截说明
        err = f"执行引擎失败: {type(e).__name__}"
        return {
            "context_data": [],
            "draft_content": "（草稿生成失败，已触发拦截流程）",
            "errors": _append_errors(state, [err]),
        }


async def node_audit_gatekeeper(state: AgentState) -> Dict[str, Any]:
    """
    合规审计：校验 draft_content 与 context_data 冲突，写回 is_compliant/final_output/errors。
    """
    draft_content = state["draft_content"]
    context_data = state["context_data"]

    try:
        is_compliant, audit_errors, final_output = await llm_client.audit_compliance(draft_content, context_data)
        merged_errors = _append_errors(state, [str(e) for e in audit_errors])
        return {"is_compliant": is_compliant, "errors": merged_errors, "final_output": final_output}
    except Exception as e:
        err = f"合规审计失败: {type(e).__name__}"
        merged_errors = _append_errors(state, [err])
        return {
            "is_compliant": False,
            "errors": merged_errors,
            "final_output": "（审计失败，已拦截展示）",
        }

