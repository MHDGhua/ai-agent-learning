"""
API工厂类 - 负责API的创建和管理
"""
import os
from typing import Dict, Any, Optional
from app.config.combined_config import API_CLIENT_CONFIG, MAGIC_TOWER_API_CONFIG
import aiohttp
import asyncio

class APIFactory:
    """API工厂类"""
    
    @staticmethod
    def create_api_client(client_type: str) -> Optional[Any]:
        """
        创建API客户端
        
        Args:
            client_type: 客户端类型 ("local", "magic_tower")
            
        Returns:
            API客户端实例
        """
        if client_type == "local":
            return LocalAPIClient()
        elif client_type == "magic_tower":
            return MagicTowerAPIClient()
        else:
            raise ValueError(f"未知的API客户端类型: {client_type}")
    
    @staticmethod
    def get_available_apis() -> list:
        """获取可用的API列表"""
        return [
            client_name 
            for client_name, config in API_CLIENT_CONFIG["clients"].items() 
            if config["enabled"]
        ]

class LocalAPIClient:
    """本地API客户端"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
    
    async def call(self, endpoint: str, data: dict) -> dict:
        """调用本地API"""
        # 实现本地API调用逻辑
        return {"status": "success", "message": "本地API调用成功", "data": data}

class MagicTowerAPIClient:
    """魔塔社区API客户端"""
    
    def __init__(self):
        self.base_url = MAGIC_TOWER_API_CONFIG["base_url"]
        self.api_key = MAGIC_TOWER_API_CONFIG["api_key"]
    
    async def call(self, endpoint: str, data: dict) -> dict:
        """调用魔塔社区API"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                async with session.post(
                    f"{self.base_url}{endpoint}",
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=MAGIC_TOWER_API_CONFIG["timeout"])
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"status": "error", "message": f"API调用失败，状态码: {response.status}"}
        except Exception as e:
            return {"status": "error", "message": f"API调用异常: {str(e)}"}