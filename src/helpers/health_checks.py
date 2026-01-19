from src.helpers.models_management import check_ollama_models, check_embedding_model
from src.helpers.qdrant_management import check_collections


async def create_health_report():
    """Проверка состояния:

    1. qdrant и его коллекции
    2. ollama и её модели
    3. модель эмбеддингов
     
    Returns:
        Dict: Словарь с информацией о статусе каждого компонента.
    """

    report = {}

    qdrant_status = await check_collections()

    if any(status == "Missing ❌" for status in qdrant_status.values()):
        report["qdrant"] = {"status": "❌ Missing collections", "details": qdrant_status}
    else:
        report["qdrant"] = {"status": "✅ OK", "details": qdrant_status}

    ollama_status = await check_ollama_models()

    if any(status == "Missing ❌" for status in ollama_status.values()):
        report["ollama"] = {"status": "❌ Missing models", "details": ollama_status}
    else:
        report["ollama"] = {"status": "✅ OK", "details": ollama_status}

    embedding_status = await check_embedding_model()

    if any(status == "Missing ❌" for status in embedding_status.values()):
        report["embedding"] = {"status": "❌ Missing model", "details": embedding_status}
    else:
        report["embedding"] = {"status": "✅ OK", "details": embedding_status}

    return report
