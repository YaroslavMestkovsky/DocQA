from src.helpers.models_management import check_ollama_models
from src.helpers.models_management import check_embedding_model
from src.helpers.qdrant_management import check_collections


def create_health_report():
    """Проверка состояния:

    1. qdrant и его коллекции
    2. ollama и её модели
    3. модели эмбединга
    """

    report = {}

    missing_qdrant_collections = check_collections()
    missing_ollama_models = check_ollama_models()
    missing_embedding_models = check_embedding_model()

    if missing_qdrant_collections:
        report["qdrant"] = "Missing collections ❌"
    else:
        report["qdrant"] = "OK ✅"


    if missing_ollama_models:
        report["ollama"] = "Missing models ❌"
    else:
        report["ollama"] = "OK ✅"

    if missing_embedding_models:
        report["embedding"] = "Missing models ❌"
    else:
        report["embedding"] = "OK ✅"

    return report
