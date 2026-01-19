from typing import List, Dict

from src.managers.qdrant import qdrant_manager
from src.logging.logger import logger
from src.helpers.configs_hub import qdrant_config


def check_collections() -> Dict:
    """Проверка наличия коллекций qdrant в соответствии с конфигом.
    
    Returns:
        Dict: Словарь с информацией о статусе каждой коллекции.
    """

    existing_collections = [col.name for col in qdrant_manager.get_collections().collections]
    report = {}

    for collection_name in qdrant_config.qdrant.collections.__dict__.keys():
        if collection_name in existing_collections:
            report[collection_name] = "OK ✅"
            logger.info(f"Коллекция {collection_name} присутствует в qdrant.")
        else:
            report[collection_name] = "Missing ❌"
            logger.warning(f"Коллекция {collection_name} не найдена в qdrant.")

    return report


def create_collections() -> Dict:
    """Создание коллекций, которых ещё нет в qdrant."""

    collections = qdrant_config.qdrant.collections
    created_collections = []
    existing_collections = [collection.name for collection in qdrant_manager.get_collections().collections]

    for collection_name in collections.__dict__.keys():
        if collection_name not in existing_collections:
            qdrant_manager.create_collection(
                collection_name,
                getattr(collections, collection_name).vector_size,
            )
            created_collections.append(collection_name)

    return {"created_collections": created_collections}
