from typing import Optional, List, Any, Dict

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    FieldCondition,
    MatchValue,
    Filter,
)

from src.dataclasses.embedding import SearchResult
from src.helpers.configs_hub import qdrant_config
from src.logging.logger import logger
from src.web.models.enums import FileType


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

    def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        file_types: Optional[List[FileType]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Поиск похожих документов. # todo добавить реранкер!

        Args:
            query_embedding: Вектор запроса
            limit: Максимальное количество результатов
            score_threshold: Порог схожести
            file_types: Фильтр по типам файлов
            metadata_filter: Фильтр по метаданным

        Returns:
            Список результатов поиска
        """

        try:
            # Построение фильтра
            filter_conditions = []

            if file_types:
                file_type_values = [ft.value for ft in file_types]

                for file_type_value in file_type_values:
                    filter_conditions.append(
                        FieldCondition(
                            key="file_type",
                            match=MatchValue(value=file_type_value),
                        ),
                )

            if metadata_filter:
                for key, value in metadata_filter.items():
                    filter_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        ),
                    )

            # Выполнение поиска
            search_filter = Filter(should=filter_conditions) if filter_conditions else None

            search_results = self.client.query_points(
                collection_name=qdrant_config.defaults.default_collection,
                query=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter,
            )

            # Преобразование результатов
            results = []

            for _result in search_results:
                result = _result[1][0]

                if result.score >= score_threshold:
                    # Собираем +- 10 результатов от полученного.
                    chunk_index = result.payload.get('chunk_index')
                    chunk_filter = Filter(
                        must=[
                            {
                                "key": "chunk_index",  # путь к полю в payload
                                "range": {
                                    "gte": chunk_index - qdrant_config.defaults.shift,
                                    "lte": chunk_index + qdrant_config.defaults.shift,
                                },
                            },
                        ],
                    )

                    points, _ = self.client.scroll(
                        collection_name=qdrant_config.defaults.default_collection,
                        scroll_filter=chunk_filter,
                        limit=100,
                        with_payload=True,
                    )

                    search_result = SearchResult(
                        ids=[point.id for point in points],
                        chunks=sorted([point.payload.get("chunk_index") for point in points]),
                        file_paths=list(set((point.payload.get("file_path", "") for point in points))),
                        file_types=list(set((FileType(point.payload.get("file_type", "document")) for point in points))),
                        texts=', '.join([point.payload.get("text", "") for point in points]),
                        score=result.score,
                    )
                    results.append(search_result)

            return results

        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}", exc_info=True)
            return []

    def close(self):
        """Закрытие соединения с Qdrant."""

        try:
            self.client.close()
            logger.debug("Соединение с qdrant закрыто.")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения с qdrant: {e}")
            raise


qdrant_manager = QdrantManager()

