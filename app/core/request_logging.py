import logging
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI, Request

logger = logging.getLogger("lerap.api.requests")


def _configure_request_logger(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_log_path = str(log_path.resolve())

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler) and handler.baseFilename == resolved_log_path:
            return

    file_handler = logging.FileHandler(resolved_log_path, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s method=%(method)s path=%(path)s status=%(status)s duration_ms=%(duration_ms).2f")
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)


def register_request_logging(app: FastAPI, log_path: Path) -> None:
    _configure_request_logger(log_path)

    @app.middleware("http")
    async def api_request_logger(request: Request, call_next):  # type: ignore[no-untyped-def]
        start = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = (perf_counter() - start) * 1000
            logger.info(
                "api_request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status_code,
                    "duration_ms": duration_ms,
                },
            )
