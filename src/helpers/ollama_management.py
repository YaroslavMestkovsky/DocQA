import json
import requests

from typing import Dict

from src.helpers.configs_hub import ollama_config


def get_model_name(_model_info):
    return _model_info["name"].split(":")[0]


def get_models() -> Dict:
    """Получение списка загруженных моделей."""

    response = requests.get(ollama_config.ollama.models_list_url)

    if response.status_code == requests.codes.ok:
        result = response.json()
    else:
        result = {"error": f"Ошибка {response.status_code}: {response.text}"}

    return result


def check_models():
    """Проверка наличия моделей в соответствии с конфигом."""

    missing_models = []
    existing_models = get_models()
    names = [get_model_name(model) for model in existing_models["models"]]

    for model_name in ollama_config.ollama.models.as_dict().values():
        if model_name not in names:
            missing_models.append(model_name)

    return missing_models


def pull_model(name):
    """Загрузка новой модели."""

    models = get_models()

    if name in [get_model_name(model) for model in models["models"]]:
        result = {"error": "Такая модель уже загружена."}
    else:
        response = requests.post(
            ollama_config.ollama.model_pull_url,
            data=json.dumps({"name": name}),
            stream=True,
        )

        if response.status_code == requests.codes.ok:
            current_models = get_models()

            try:
                model_info = (model for model in current_models["models"] if name == get_model_name(model)).__next__()
                result = {"uploaded_model": model_info}
            except StopIteration:
                result = {"error": "Произошла непредвиденная ошибка."}
        else:
            result = {"error": f"Ошибка {response.status_code}: {response.text}"}

    return result
