"""
API 配置兼容层。

历史脚本仍然从 app.config.api_config 导入，这里统一转发到 combined_config，
避免旧入口直接报错。
"""

from .combined_config import API_CLIENT_CONFIG, API_ENDPOINTS

__all__ = ["API_CLIENT_CONFIG", "API_ENDPOINTS"]
