from typing import List, Dict

from src.managers.qdrant import qdrant_manager
from src.logging.logger import logger
from src.helpers.configs_hub import qdrant_config


def check_collections() -> List:
    """Проверка наличия коллекций qdrant в соответствии с конфигом."""

    existing_collections = [col.name for col in qdrant_manager.get_collections().collections]
    collections_to_create = []

    for collection_name in qdrant_config.qdrant.collections.__dict__.keys():
        if collection_name not in existing_collections:
            collections_to_create.append(collection_name)
            logger.warning(f"Коллекция {collection_name} не найдена в qdrant.")

    if not collections_to_create:
        logger.info("Все коллекции присутствуют в qdrant.")

    return collections_to_create


def create_collections() -> Dict:
    """Создание коллекций, которых ещё нет в qdrant."""

    collections_to_create = created_collections = check_collections()

    for collection_name in collections_to_create:
        collection = getattr(qdrant_config.qdrant.collections, collection_name)
        qdrant_manager.create_collection(collection.name, collection.vector_size)

    return {"created_collections": created_collections}
