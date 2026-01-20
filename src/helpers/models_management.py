import json
import requests

from typing import Dict
from functools import lru_cache
from sentence_transformers import SentenceTransformer

from src.helpers.configs_hub import ollama_config
from src.helpers.configs_hub import embedding_config


def get_model_name(_model_info):
    return _model_info["name"].split(":")[0]


async def get_ollama_models() -> Dict:
    """Получение списка загруженных моделей ollama."""

    response = requests.get(ollama_config.ollama.models_list_url)

    if response.status_code == requests.codes.ok:
        result = response.json()
    else:
        result = {"error": f"Ошибка {response.status_code}: {response.text}"}

    return result


async def check_ollama_models():
    """Проверка наличия моделей ollama в соответствии с конфигом.
    
    Returns:
        Dict: Словарь с информацией о статусе каждой модели.
    """

    report = {}
    existing_models = await get_ollama_models()
    names = [get_model_name(model) for model in existing_models["models"]]

    for model_name in ollama_config.ollama.models.as_dict().values():
        if model_name in names:
            report[model_name] = "OK ✅"
        else:
            report[model_name] = "Missing ❌"

    return report


async def pull_ollama_model(name):
    """Загрузка новой модели."""

    models = await get_ollama_models()

    if name in [get_model_name(model) for model in models["models"]]:
        result = {"error": "Такая модель уже загружена."}
    else:
        response = requests.post(
            ollama_config.ollama.model_pull_url,
            data=json.dumps({"name": name}),
            stream=True,
        )

        if response.status_code == requests.codes.ok:
            current_models = await get_ollama_models()

            try:
                model_info = (model for model in current_models["models"] if name == get_model_name(model)).__next__()
                result = {"uploaded_model": model_info}
            except StopIteration:
                result = {"error": "Произошла непредвиденная ошибка."}
        else:
            result = {"error": f"Ошибка {response.status_code}: {response.text}"}

    return result


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Возвращает единственный экземпляр модели эмбеддингов (singleton)."""

    model_name = embedding_config.models.embedding
    model = SentenceTransformer(model_name)
    model.save('/opt/models/multilingual-e5-large')

    return model


async def check_embedding_model():
    """Проверяет наличие экземпляра модели эмбеддингов в кэше.
    
    Returns:
        Dict: Словарь с информацией о статусе модели эмбеддингов.
    """

    cache_info = get_embedding_model.cache_info()
    model_name = embedding_config.models.embedding
    
    if cache_info.misses > 0:
        return {model_name: "OK ✅"}
    else:
        return {model_name: "Missing ❌"}
