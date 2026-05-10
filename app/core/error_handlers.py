import logging
import os
import traceback
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import LERAPError

logger = logging.getLogger("lerap.api")


def _is_development() -> bool:
    environment = os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or "development"
    return environment.lower() not in {"prod", "production"}


def _error_response(status_code: int, error: str, detail: Any) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
            "detail": detail,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(LERAPError)
    async def lerap_error_handler(request: Request, exc: LERAPError) -> JSONResponse:
        return _error_response(
            status_code=exc.status_code,
            error=exc.user_message,
            detail=exc.detail,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail if exc.detail else "请求失败。"
        return _error_response(status_code=exc.status_code, error=str(detail), detail=detail)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        detail = exc.errors() if _is_development() else "请求参数不符合要求。"
        return _error_response(status_code=422, error="请求参数错误", detail=detail)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled API error: %s %s", request.method, request.url.path)
        if _is_development():
            detail: Any = {
                "type": exc.__class__.__name__,
                "message": str(exc),
                "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__),
            }
        else:
            detail = "服务暂时不可用，请稍后重试。"
        return _error_response(status_code=500, error="服务器内部错误", detail=detail)
