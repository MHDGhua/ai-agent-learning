"""
系统基础配置
"""
import os
from typing import Optional

# 导入合并配置
from .combined_config import (
    MODEL_NAME, TEMPERATURE, MAX_TOKENS,
    OPENAI_API_KEY, MAGIC_TOWER_API_KEY, DEEPSEEK_API_KEY,
    REQUEST_TIMEOUT, MAX_RETRIES,
    API_BASE_URL,
    MAGIC_TOWER_API_CONFIG,
    LOCAL_API_CONFIG,
    API_CLIENT_CONFIG,
    API_ENDPOINTS
)

# 系统基本信息
APP_NAME = "重庆劳动法专家系统"
VERSION = "1.2.0"

# API配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/runtime/lerap_app.db")

# API工厂配置
DEFAULT_API = os.getenv("DEFAULT_API", "local")
ENABLE_API_SWITCHING = os.getenv("ENABLE_API_SWITCHING", "True").lower() == "true"

# LLM提供商配置
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, magic_tower, deepseek
