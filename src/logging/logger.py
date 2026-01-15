import sys
from loguru import logger  # noqa F401


def configure_logging(log_level: str = "INFO", log_file: str = None):
    """Настраивает логирование."""
    logger.remove()

    # Настройка формата логов
    format_str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Добавляем вывод в stdout
    logger.add(
        sys.stdout,
        level=log_level,
        format=format_str,
        colorize=True,
    )

    # Добавляем вывод в файл, если указан
    if log_file:
        logger.add(
            log_file,
            level=log_level,
            format=format_str,
            colorize=False,
            rotation="10 MB",
            retention="7 days",
        )

    logger.info("Логирование настроено")
