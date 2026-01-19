from fastapi import APIRouter, Query
from src.helpers.models_management import (
    get_ollama_models,
    pull_ollama_model,
    check_ollama_models,
)

from src.services.ollama import OllamaService

router = APIRouter()


@router.get("/get_models_list", summary="Get all ollama models")
async def get_all() -> dict:
    return await get_ollama_models()


@router.get("/check_models", summary="Check if all models from config uploaded")
async def check_models_exists() -> dict:
    return {"models_status": await check_ollama_models()}


@router.post("/pull_model", summary="Pull ollama model by name")
async def pull_model_by_name(name: str = Query(..., description="Model name to pull")) -> dict:
    return await pull_ollama_model(name)


@router.post("/ask_model", summary="Ask model with context")
async def ask_model(query: str, context: str) -> dict:
    """Запрос к модели Ollama с учетом контекста.
     
     Args:
         query (str): Вопрос пользователя.
         context (str): Контекст для формирования ответа.
      
     Returns:
         dict: Ответ от модели или информация об ошибке.
    """
    return await OllamaService.ask_model(query, context)
