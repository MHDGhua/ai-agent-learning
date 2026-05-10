import json
import os
import re
from typing import List, Literal, Tuple, Any

from dotenv import load_dotenv
from loguru import logger
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI, ChatOpenAI

load_dotenv()

# 导入合并配置
from app.config.combined_config import (
    MODEL_NAME, TEMPERATURE, MAX_TOKENS,
    OPENAI_API_KEY, MAGIC_TOWER_API_KEY, DEEPSEEK_API_KEY,
    API_BASE_URL
)

Intent = Literal["draft", "audit", "query"]

# 支持的模型提供商
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")  # local, openai, magic_tower, deepseek


def _is_configured_key(value: str) -> bool:
    value = (value or "").strip()
    return bool(value) and not value.startswith("your_") and value.lower() not in {"none", "null", "changeme"}


class _LocalLLMFallback:
    """离线兜底：保证测试和基础演示可运行。"""

    async def ainvoke(self, messages: List[Any]) -> Any:
        text = messages[-1].content if messages else ""
        return type("Resp", (), {"content": text})()

class LLMClient:
    def __init__(self) -> None:
        self._llm = None

    def _use_local_logic(self) -> bool:
        provider = LLM_PROVIDER.lower()
        return provider == "local" or (provider == "deepseek" and not _is_configured_key(DEEPSEEK_API_KEY))

    def _get_llm(self):
        if self._llm is not None:
            return self._llm

        provider = LLM_PROVIDER.lower()
        if provider == "local":
            self._llm = _LocalLLMFallback()
            return self._llm

        # 根据配置选择LLM提供商
        if provider == "azure":
            # Azure OpenAI 配置
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_KEY")
            deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

            if not endpoint or not api_key or not deployment:
                raise RuntimeError("未配置 Azure OpenAI 环境变量：AZURE_OPENAI_ENDPOINT/AZURE_OPENAI_KEY/AZURE_OPENAI_DEPLOYMENT")

            self._llm = AzureChatOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                azure_deployment=deployment,
                api_version=api_version,
                streaming=False,
            )
        elif provider == "magic_tower":
            # 魔塔社区 API 配置
            if not MAGIC_TOWER_API_KEY:
                raise RuntimeError("未配置魔塔社区 API 密钥")
                
            self._llm = ChatOpenAI(
                model=MODEL_NAME,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                api_key=MAGIC_TOWER_API_KEY,
                base_url="https://api.magic-tower.com/v1",  # 魔塔社区 API 地址
            )
        elif provider == "deepseek":
            # DeepSeek API 配置
            if not _is_configured_key(DEEPSEEK_API_KEY):
                logger.warning("未配置 DeepSeek API 密钥，当前回退到本地模式。")
                self._llm = _LocalLLMFallback()
                return self._llm
                
            self._llm = ChatOpenAI(
                model=os.getenv("DEEPSEEK_MODEL", MODEL_NAME or "deepseek-v4-flash"),
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                api_key=DEEPSEEK_API_KEY,
                base_url=os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com"),
            )
        else:
            # 默认使用 OpenAI
            if not OPENAI_API_KEY:
                raise RuntimeError("未配置 OpenAI API 密钥")
                
            self._llm = ChatOpenAI(
                model=MODEL_NAME,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                api_key=OPENAI_API_KEY,
                base_url=API_BASE_URL,
            )
            
        return self._llm

    def _extract_case_signals(self, text: str) -> dict:
        lower = text.lower()
        if any(k in lower for k in ["申请书", "起草", "生成", "文书", "draft"]):
            intent = "draft"
        elif any(k in lower for k in ["审计", "审查", "冲突", "audit"]):
            intent = "audit"
        else:
            intent = "query"
        return {"intent": intent}

    async def classify_intent(self, user_input: str) -> Intent:
        """
        仅输出意图字符串（draft/audit/query）以便状态机可确定性推进。
        """

        if self._use_local_logic():
            lower = user_input.lower()
            if any(k in lower for k in ["申请书", "答辩书", "证据清单", "代理词", "文书", "生成"]):
                return "draft"
            if any(k in lower for k in ["审计", "审查", "核查", "对抗"]):
                return "audit"
            return "query"

        llm = self._get_llm()
        allowed = ["draft", "audit", "query"]
        prompt = (
            "你是 L-ERAP PRO 的意图路由器。\n"
            "用户输入将触发三类任务：\n"
            "draft：需要生成文书初稿/草案内容。\n"
            "audit：需要对草稿进行合规审计/冲突检查。\n"
            "query：只需要检索/解释相关法律条文或案例。\n\n"
            f"要求：只输出一个字符串，必须且只能是以下之一之一：{allowed}。\n"
            f"用户输入：{user_input}\n"
        )

        # LangChain 支持异步 invoke
        resp = await llm.ainvoke([HumanMessage(content=prompt)])
        text = (resp.content or "").strip().lower()
        if text not in allowed:
            # 不可解析时降级到 query
            logger.warning(f"意图解析失败，降级为 query。原始输出: {text}")
            return "query"
        return text  # type: ignore[return-value]

    async def generate_draft(self, user_input: str, intent: str, context_data: List[str]) -> str:
        """
        生成 draft_content。要求引用 context_data 的要点以便后续 auditor 做冲突检测。
        """

        if self._use_local_logic():
            context_block = "；".join(context_data[:3]) if context_data else "无检索上下文"
            return (
                f"根据当前输入，我建议按{intent}方向处理。"
                f"已结合上下文：{context_block}。"
                "请补充时间、单位名称、工资标准、证据清单和诉求金额后再提交。"
            )

        llm = self._get_llm()
        context_block = "\n\n".join([f"[{i+1}] {c}" for i, c in enumerate(context_data)]) if context_data else "（无召回上下文）"

        prompt = (
            "你是 L-ERAP PRO 的文书生成器，目标是生成可审计的草稿内容。\n"
            f"意图(intent)={intent}。\n\n"
            "约束：\n"
            "1) 必须基于“上下文(context_data)”的要点进行编写与解释。\n"
            "2) 草稿中要明确标出你使用了哪些上下文条目（例如“引用来源[1][2]”）。\n"
            "3) 输出只包含草稿正文，不要输出工具调用过程。\n\n"
            f"用户输入：{user_input}\n\n"
            f"上下文(context_data)：\n{context_block}\n"
        )

        resp = await llm.ainvoke([HumanMessage(content=prompt)])
        content = resp.content or ""
        return content.strip() or "（草稿为空，可能是上游 LLM 生成失败）"

    async def audit_compliance(self, draft_content: str, context_data: List[str]) -> Tuple[bool, List[str], str]:
        """
        合规审计：输出稳定 JSON 以便解析。
        """

        if self._use_local_logic():
            errors = []
            if "补充" in draft_content or "缺失" in draft_content:
                errors.append("草稿内容仍需补充关键事实")
            final_output = draft_content if not errors else "请先补齐案件事实后再提交。"
            return (len(errors) == 0, errors, final_output)

        llm = self._get_llm()
        context_block = "\n\n".join([f"[{i+1}] {c}" for i, c in enumerate(context_data)]) if context_data else "（无召回上下文）"

        prompt = (
            "你是 L-ERAP PRO 的合规审计器。你的任务是检查草稿与上下文之间是否存在明显冲突。\n"
            "冲突判定的最小要求：\n"
            "1) 如果草稿声称的关键事实/法律适用与 context_data 明显不一致，则判定不合规。\n"
            "2) 如果无法从 context_data 充分支撑草稿关键结论，则给出不足以支撑的错误。\n\n"
            "输出要求（严格 JSON，无多余文本）：\n"
            "{\n"
            '  "is_compliant": true/false,\n'
            '  "errors": ["错误1", "错误2"],\n'
            '  "final_output": "审计后的对外展示内容"\n'
            "}\n\n"
            f"草稿(draft_content)：\n{draft_content}\n\n"
            f"上下文(context_data)：\n{context_block}\n"
        )

        resp = await llm.ainvoke([HumanMessage(content=prompt)])
        raw = (resp.content or "").strip()

        # 容错：尝试提取 JSON 对象
        try:
            parsed = json.loads(raw)
        except Exception:
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(raw[start : end + 1])
            else:
                raise RuntimeError("合规审计输出无法解析为 JSON")

        is_compliant = bool(parsed.get("is_compliant", False))
        errors = parsed.get("errors", []) or []
        if not isinstance(errors, list):
            errors = [str(errors)]
        final_output = parsed.get("final_output", "") or ""
        final_output = str(final_output).strip() or "（审计输出为空）"
        return is_compliant, [str(e) for e in errors], final_output

    async def generate_text(self, prompt: str) -> str:
        """兼容旧 Agent 接口。"""
        if self._use_local_logic():
            return "本地模式下已生成基础分析结果。"
        llm = self._get_llm()
        resp = await llm.ainvoke([HumanMessage(content=prompt)])
        return str(resp.content or "").strip()


_client = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client


async def classify_intent(user_input: str) -> Intent:
    return await get_llm_client().classify_intent(user_input)


async def generate_draft(user_input: str, intent: str, context_data: List[str]) -> str:
    return await get_llm_client().generate_draft(user_input, intent, context_data)


async def audit_compliance(draft_content: str, context_data: List[str]) -> Tuple[bool, List[str], str]:
    return await get_llm_client().audit_compliance(draft_content, context_data)

