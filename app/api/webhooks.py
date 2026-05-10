import asyncio
from typing import Any, Dict

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel
from loguru import logger

from app.core.graph import run_task


class WebhookRequest(BaseModel):
    task_id: str
    user_input: str


def register_routes(app: FastAPI) -> None:
    @app.post("/webhooks/callback")
    async def callback(req: WebhookRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """
        手册要求：请求必须快速返回 200 + task_id；真正推演放到后台。
        """
        background_tasks.add_task(_run_task_background, req.task_id, req.user_input)
        return {"task_id": req.task_id, "status": "accepted"}


def _run_task_background(task_id: str, user_input: str) -> None:
    """
    BackgroundTasks 在同步上下文执行时更安全；此处通过 asyncio.run 开新事件循环。
    """

    try:
        asyncio.run(run_task(task_id=task_id, user_input=user_input))
    except Exception as e:
        logger.error(f"后台任务失败 task_id={task_id}: {type(e).__name__}")

