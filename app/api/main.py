"""
兼容入口。

历史代码和文档中同时存在 `app.main` 与 `app.api.main` 两个启动路径。
统一转发到 `app.main`，避免部署和测试时出现行为不一致。
"""

from app.main import app, create_app

__all__ = ["app", "create_app"]

