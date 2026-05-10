"""Optional observability hooks for backend workflows."""

import os
from typing import Any, Callable, Dict


def _env_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


try:
    from langsmith import traceable as _langsmith_traceable
except Exception:  # pragma: no cover - optional dependency fallback
    _langsmith_traceable = None


def traceable_case(name: str, run_type: str = "chain") -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Trace a backend case workflow when LangSmith is configured.

    LangSmith remains opt-in through environment variables. Without a configured
    LangSmith installation this decorator is a no-op, so local tests stay stable.
    """

    if _langsmith_traceable is None:
        return lambda func: func
    return _langsmith_traceable(name=name, run_type=run_type)


def langsmith_status() -> Dict[str, Any]:
    """Return safe observability status without exposing secrets."""

    return {
        "provider": "langsmith",
        "tracing_enabled": _env_enabled("LANGSMITH_TRACING"),
        "api_key_configured": bool(os.getenv("LANGSMITH_API_KEY")),
        "project": os.getenv("LANGSMITH_PROJECT") or "default",
        "endpoint": os.getenv("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com",
        "dependency_available": _langsmith_traceable is not None,
        "privacy_note": "启用后，请求输入、模型调用和输出可能发送到 LangSmith；生产环境应先确认脱敏策略。",
    }
