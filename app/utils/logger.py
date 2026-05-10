import os
from pathlib import Path

from loguru import logger


def setup_logger() -> None:
    """
    初始化统一日志配置，避免在各模块重复配置导致输出不一致。
    """

    console_level = os.getenv("LOG_LEVEL", "INFO").upper()
    file_level = os.getenv("LOG_FILE_LEVEL", "DEBUG").upper()
    log_file = Path(os.getenv("LOG_FILE", "logs/lerap_pro.log"))
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # 避免重复 add handler
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=console_level,
        colorize=False,
        format="{time} | {level} | {message}",
    )
    # 文件日志用于排查；不会打印任何敏感信息（由业务层保证）。
    logger.add(
        str(log_file),
        level=file_level,
        rotation=os.getenv("LOG_ROTATION", "20 MB"),
        retention=os.getenv("LOG_RETENTION", "7 days"),
        encoding="utf-8",
        format="{time} | {level} | {message}",
    )

