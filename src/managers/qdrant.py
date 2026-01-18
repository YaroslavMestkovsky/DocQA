from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
)

from src.helpers.configs_hub import qdrant_config
from src.logging.logger import logger


class QdrantManager:
    """Менеджер для работы с Qdrant."""

    def __init__(self):
        self.client: QdrantClient = QdrantClient(host=qdrant_config.qdrant.host, port=qdrant_config.qdrant.port)

    def get_collections(self):
        """Получение коллекций qdrant."""
        return self.client.get_collections()

    def create_collection(self, name, size):
        """Создание коллекции qdrant."""

        try:
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=size,
                    distance=Distance.COSINE,
                ),
            )
            logger.debug(f"Коллекция {name} создана.")
        except Exception as e:
            logger.error(f"Ошибка при создании коллекции {name}: {e}")

    def delete_collection(self, name):
        """Удаление коллекции qdrant."""

        try:
            self.client.delete_collection(name)
            logger.debug(f"Коллекция '{name}' удалена.")

        except Exception as e:
            logger.error(f"Ошибка при удалении коллекции: {e}")
            raise

    def close(self):
        """Закрытие соединения с Qdrant."""

        try:
            self.client.close()
            logger.debug("Соединение с qdrant закрыто.")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения с qdrant: {e}")
            raise


qdrant_manager = QdrantManager()

