from fastapi import FastAPI

from src.helpers.configs_hub import fastapi_config
from src.web.api.router import api_router
from src.web.middlewares.error_handler import ErrorHandlerMiddleware, http_error_handler
from src.logging.logger import configure_logging


def create_app() -> FastAPI:
    # Настройка логирования
    configure_logging(
        log_level="INFO",
        log_file=fastapi_config.web.log_file,
    )
    
    _app = FastAPI(
        title="DocQA Web API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # Добавляем middleware для обработки ошибок
    _app.add_middleware(ErrorHandlerMiddleware)
    
    # Добавляем обработчик HTTP ошибок
    _app.add_exception_handler(Exception, http_error_handler)

    _app.include_router(api_router)

    return _app


# ASGI entrypoint
app = create_app()
