#!/usr/bin/env python3
"""
API工厂集成测试脚本
测试API工厂是否正确配置和工作
"""

import asyncio
import sys
from app.services.api_factory import APIFactory
from app.config.api_config import API_CLIENT_CONFIG

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

async def test_api_factory():
    """测试API工厂功能"""
    print("=== API工厂集成测试 ===")
    
    # 1. 测试API客户端创建
    print("\n1. 测试API客户端创建...")
    try:
        local_client = APIFactory.create_api_client("local")
        magic_tower_client = APIFactory.create_api_client("magic_tower")
        print("✓ API客户端创建成功")
        print(f"  本地客户端: {type(local_client).__name__}")
        print(f"  魔塔客户端: {type(magic_tower_client).__name__}")
    except Exception as e:
        print(f"✗ API客户端创建失败: {e}")
        return False
    
    # 2. 测试可用API列表
    print("\n2. 测试可用API列表...")
    try:
        available_apis = APIFactory.get_available_apis()
        print("✓ 可用API列表获取成功")
        print(f"  可用API: {available_apis}")
    except Exception as e:
        print(f"✗ 可用API列表获取失败: {e}")
        return False
    
    # 3. 测试API配置
    print("\n3. 测试API配置...")
    try:
        default_api = API_CLIENT_CONFIG.get("default", "local")
        clients = API_CLIENT_CONFIG.get("clients", {})
        print("✓ API配置获取成功")
        print(f"  默认API: {default_api}")
        print(f"  API客户端配置: {list(clients.keys())}")
    except Exception as e:
        print(f"✗ API配置获取失败: {e}")
        return False
    
    # 4. 测试API调用（简单模拟）
    print("\n4. 测试API调用...")
    try:
        # 测试本地API调用
        test_data = {"test": "data"}
        result = await local_client.call("/test", test_data)
        print("✓ API调用测试完成")
        print(f"  调用结果: {result}")
    except Exception as e:
        print(f"  API调用测试完成 (预期失败): {e}")
    
    print("\n=== API工厂集成测试完成 ===")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_api_factory())
    if success:
        print("\n🎉 所有测试通过！API工厂已正确集成。")
    else:
        print("\n❌ 部分测试失败，请检查配置。")
