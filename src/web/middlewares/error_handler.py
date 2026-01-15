"""Middleware для централизованной обработки ошибок."""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки ошибок и логирования."""
    
    async def dispatch(self, request: Request, call_next):
        """Обрабатывает запрос и перехватывает ошибки."""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса {request.url}: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Внутренняя ошибка сервера", "details": str(e)},
            )


async def http_error_handler(request: Request, exc):
    """Обработчик HTTP ошибок."""
    logger.error(f"HTTP ошибка {exc.status_code} для {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )