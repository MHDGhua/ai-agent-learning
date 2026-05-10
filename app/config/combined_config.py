"""
合并的配置文件 - 整合 LLM 和 API 配置
"""
import os
from typing import Optional

# LLM 基础配置
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

# API 密钥配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAGIC_TOWER_API_KEY = os.getenv("MAGIC_TOWER_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# 超时配置
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# 模型特定配置
GPT4_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
}

# API 端点配置
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")

# 魔塔社区 API 配置
MAGIC_TOWER_API_CONFIG = {
    "base_url": "https://api.magic-tower.com",
    "api_key": MAGIC_TOWER_API_KEY,
    "version": "v1",
    "timeout": 30
}

# 本地 API 配置
LOCAL_API_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30
}

# API 客户端配置
API_CLIENT_CONFIG = {
    "default": "local",
    "clients": {
        "local": {
            "type": "local",
            "enabled": True
        },
        "magic_tower": {
            "type": "external",
            "enabled": True,
            "endpoint": MAGIC_TOWER_API_CONFIG["base_url"],
            "api_key": MAGIC_TOWER_API_CONFIG["api_key"]
        }
    }
}

# API 端点映射
API_ENDPOINTS = {
    "arbitration_analysis": "/api/arbitration/analyze",
    "document_generation": "/api/arbitration/generate-document",
    "cost_estimation": "/api/arbitration/estimate-cost",
    "success_prediction": "/api/arbitration/predict-success-rate"
}