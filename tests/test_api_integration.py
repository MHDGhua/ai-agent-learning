#!/usr/bin/env python3
"""API 工厂集成测试。"""

import asyncio
import os
import unittest

os.environ.setdefault("LLM_PROVIDER", "local")

from app.config.api_config import API_CLIENT_CONFIG
from app.services.api_factory import APIFactory


class APIFactoryIntegrationTests(unittest.TestCase):
    def test_available_clients_and_default_config(self):
        available_apis = APIFactory.get_available_apis()
        self.assertIn("local", available_apis)
        self.assertIn("magic_tower", available_apis)
        self.assertEqual(API_CLIENT_CONFIG.get("default"), "local")

    def test_local_client_echoes_payload(self):
        local_client = APIFactory.create_api_client("local")

        async def _run():
            result = await local_client.call("/test", {"test": "data"})
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["data"], {"test": "data"})

        asyncio.run(_run())

    def test_magic_tower_client_is_constructible(self):
        magic_tower_client = APIFactory.create_api_client("magic_tower")
        self.assertEqual(type(magic_tower_client).__name__, "MagicTowerAPIClient")

    def test_unknown_client_type_rejected(self):
        with self.assertRaises(ValueError):
            APIFactory.create_api_client("unknown")


if __name__ == "__main__":
    unittest.main(verbosity=2)
