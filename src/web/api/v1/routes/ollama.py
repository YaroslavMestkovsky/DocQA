import requests
import json

from fastapi import APIRouter, Query
from src.helpers.models_management import (
    get_ollama_models,
    pull_ollama_model,
    check_ollama_models,
)

from src.helpers.configs_hub import ollama_config

router = APIRouter()


@router.get("/get_models_list", summary="Get all ollama models")
def get_all() -> dict:
    return get_ollama_models()


@router.get("/check_models", summary="Check if all models from config uploaded")
def check_models_exists() -> dict:
    return {"models_status": check_ollama_models()}


@router.post("/pull_model", summary="Pull ollama model by name")
def pull_model_by_name(name: str = Query(..., description="Model name to pull")) -> dict:
    return pull_ollama_model(name)


@router.post("/ask_model", summary="Ask model with context")
def ask_model(query: str, context: str) -> dict:
    """Запрос к модели Ollama с учетом контекста.
    
    Args:
        query (str): Вопрос пользователя.
        context (str): Контекст для формирования ответа.
    
    Returns:
        dict: Ответ от модели или информация об ошибке.
    """

    # Формирование промпта с учетом контекста
    prompt = ollama_config.ollama.prompt.format(query=query, context=context)
    
    # Запрос к модели
    response = requests.post(
        ollama_config.ollama.generate_url,
        data=json.dumps({
            "model": ollama_config.ollama.models.llama3,
            "prompt": prompt,
            "stream": False,
        }),
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == requests.codes.ok:
        result = response.json()
        return {"response": result.get("response", "")}
    else:
        return {"error": f"Ошибка {response.status_code}: {response.text}"}
