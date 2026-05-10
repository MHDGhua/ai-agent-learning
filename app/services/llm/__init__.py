"""
LLM service module for L-ERAP PRO.
Provides abstract interfaces and implementations for multiple LLM providers.
"""

from .base import BaseLLMClient, Intent
from .factory import LLMFactory, get_llm_client_for_node
from .azure_client import AzureLLMClient
from .modelscope_client import ModelScopeLLMClient
from .openai_client import OpenAILLMClient
from .deepseek_client import DeepSeekLLMClient
from .local_client import LocalLLMClient

__all__ = [
    "BaseLLMClient",
    "Intent",
    "LLMFactory",
    "get_llm_client_for_node",
    "AzureLLMClient",
    "ModelScopeLLMClient",
    "OpenAILLMClient",
    "DeepSeekLLMClient",
    "LocalLLMClient",
]