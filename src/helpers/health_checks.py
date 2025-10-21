from src.helpers.models_management import check_models
from src.helpers.qdrant_management import check_collections


def create_health_report():
    """Проверка состояния:

    1. qdrant и его коллекции
    2. ollama и её модели
    """

    report = {}

    missing_qdrant_collections = check_collections()
    missing_ollama_models = check_models()


    if missing_qdrant_collections:
        report["qdrant"] = "Missing collections ❌"
    else:
        report["qdrant"] = "OK ✅"


    if missing_ollama_models:
        report["ollama"] = "Missing models ❌"
    else:
        report["ollama"] = "OK ✅"

    return report
