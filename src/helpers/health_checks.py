from src.helpers.models_management import check_ollama_models, check_embedding_model
from src.helpers.qdrant_management import check_collections


def create_health_report():
    """Проверка состояния:

    1. qdrant и его коллекции
    2. ollama и её модели
    3. модель эмбеддингов
    """

    report = {}

    if missing_qdrant_collections := check_collections():
        report["qdrant"] = f"Missing collections ❌: {missing_qdrant_collections}"
    else:
        report["qdrant"] = "OK ✅"


    if missing_ollama_models := check_ollama_models():
        report["ollama"] = f"Missing models ❌: {missing_ollama_models}"
    else:
        report["ollama"] = "OK ✅"

    if missing_embedding_models := check_embedding_model():
        report["embedding"] = f"Missing embedding model: {missing_embedding_models} ❌"
    else:
        report["embedding"] = "OK ✅"

    return report
