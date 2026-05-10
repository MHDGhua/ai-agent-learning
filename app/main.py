"""
主应用入口
"""
import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.auth import router as auth_router
from app.api.arbitration import router as arbitration_router
from app.api.workspace import router as workspace_router
from app.api.webhooks import register_routes
from app.core.error_handlers import register_exception_handlers
from app.core.persistence import ensure_database
from app.core.request_logging import register_request_logging
from app.config.settings import VERSION
from app.utils.logger import setup_logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"
FRONTEND_INDEX = FRONTEND_DIST_DIR / "index.html" if (FRONTEND_DIST_DIR / "index.html").exists() else FRONTEND_DIR / "index.html"
API_PREFIXES = {"auth", "arbitration", "workspace", "webhooks", "healthz", "assets", "frontend", "src"}


def _parse_csv_env(name: str, default: str = "") -> List[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _configure_security_middleware(app: FastAPI) -> None:
    cors_origins = _parse_csv_env("CORS_ALLOWED_ORIGINS", "*") or ["*"]
    allow_credentials = cors_origins != ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    allowed_hosts = _parse_csv_env("ALLOWED_HOSTS", "*") or ["*"]
    if allowed_hosts != ["*"]:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)


def register_healthcheck(app: FastAPI) -> None:
    @app.get("/healthz", include_in_schema=False)
    async def healthz():
        return {"status": "ok"}


def register_frontend(app: FastAPI) -> None:
    if not FRONTEND_INDEX.exists():
        return

    static_dir = FRONTEND_DIST_DIR if FRONTEND_DIST_DIR.exists() else FRONTEND_DIR
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend-assets")
    elif (FRONTEND_DIR / "src").exists():
        app.mount("/src", StaticFiles(directory=str(FRONTEND_DIR / "src")), name="frontend-src")

    app.mount("/frontend", StaticFiles(directory=str(static_dir)), name="frontend")

    @app.get("/", include_in_schema=False)
    async def frontend_index():
        return FileResponse(FRONTEND_INDEX)

    @app.get("/assistant", include_in_schema=False)
    async def frontend_assistant():
        return FileResponse(FRONTEND_INDEX)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def frontend_spa_fallback(full_path: str):
        first_segment = full_path.split("/", 1)[0]
        if first_segment in API_PREFIXES:
            raise HTTPException(status_code=404, detail="Not Found")
        return FileResponse(FRONTEND_INDEX)


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    setup_logger()
    ensure_database()
    app = FastAPI(
        title="重庆劳动法专家系统",
        version=VERSION,
        description="专注于重庆地区劳动法的智能咨询系统"
    )
    
    _configure_security_middleware(app)
    register_request_logging(app, PROJECT_ROOT / "data" / "runtime" / "api.log")
    register_exception_handlers(app)

    # 注册API路由
    app.include_router(auth_router)
    app.include_router(arbitration_router)
    app.include_router(workspace_router)
    
    # 注册webhook路由
    register_routes(app)
    register_healthcheck(app)
    register_frontend(app)
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
