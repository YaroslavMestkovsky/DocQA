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

    collections_to_create = created_collections = check_collections()

    for collection_name in collections_to_create:
        collection = getattr(qdrant_config.qdrant.collections, collection_name)
        qdrant_manager.create_collection(collection.name, collection.vector_size)

    return {"created_collections": created_collections}
