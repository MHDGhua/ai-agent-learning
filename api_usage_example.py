#!/usr/bin/env python3
"""
API工厂使用示例
演示如何使用API工厂连接和调用不同API服务
"""

import asyncio
import sys
from app.services.api_factory import APIFactory
from app.config.api_config import API_CLIENT_CONFIG

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

async def demonstrate_api_factory():
    """演示API工厂的使用"""
    print("=== API工厂使用演示 ===")
    
    # 1. 创建API客户端
    print("\n1. 创建API客户端...")
    local_client = APIFactory.create_api_client("local")
    magic_tower_client = APIFactory.create_api_client("magic_tower")
    
    print(f"本地API客户端: {local_client}")
    print(f"魔塔API客户端: {magic_tower_client}")
    
    # 2. 获取可用API列表
    print("\n2. 可用API列表...")
    available_apis = APIFactory.get_available_apis()
    print(f"可用API: {available_apis}")
    
    # 3. 测试API调用
    print("\n3. 测试API调用...")
    
    # 测试本地API调用
    try:
        test_data = {"test": "data"}
        result = await local_client.call("/test-endpoint", test_data)
        print(f"本地API调用结果: {result}")
    except Exception as e:
        print(f"本地API调用失败: {e}")
    
    # 4. API配置信息
    print("\n4. API配置信息...")
    print(f"默认API: {API_CLIENT_CONFIG.get('default', 'local')}")
    print(f"可用API客户端: {API_CLIENT_CONFIG.get('clients', {})}")

if __name__ == "__main__":
    asyncio.run(demonstrate_api_factory())
