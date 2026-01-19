from typing import List

from sentence_transformers import SentenceTransformer

from src.dataclasses.embedding import SearchResponse
from src.helpers.models_management import get_embedding_model
from src.logging.logger import logger
from src.managers.qdrant import QdrantManager
from src.helpers.configs_hub import querier_config
from src.managers.qdrant import qdrant_manager as qm


class QueryService:
    """Сервис поиска и запросов."""

    def __init__(self, qdrant_manager: QdrantManager = qm):
        self.qdrant_manager = qdrant_manager
        self.embedding_model: SentenceTransformer = get_embedding_model()

    async def search(self, query: str, **kwargs) -> SearchResponse:
        """Поиск по базе знаний."""

        try:
            # Создание эмбеддинга запроса
            query_embedding = self._create_query_embedding(query)

            # Параметры поиска
            limit = kwargs.get('limit', querier_config.querier.processing.top_k)
            score_threshold = kwargs.get('score_threshold', 0.0)
            file_types = kwargs.get('file_types')
            metadata_filter = kwargs.get('metadata_filter')

            # Выполнение поиска
            results = self.qdrant_manager.search_similar(
                query_embedding=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                file_types=file_types,
                metadata_filter=metadata_filter,
            )
            return SearchResponse(
                query=query,
                results=results,
                total_found=len(results),
                processing_time=0.0,  # TODO: добавить измерение времени
                query_embedding=query_embedding,
            )

        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}", exc_info=True)
            return SearchResponse(
                query=query,
                results=[],
                total_found=0,
                processing_time=0.0,
                query_embedding=[],
            )

    def _create_query_embedding(self, query: str) -> List[float]:
        """Создание эмбеддинга для запроса."""

        try:
            if not query.strip():
                return [0.0] * 1024  # Пустой вектор

            embedding = self.embedding_model.encode(query)
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Ошибка при создании эмбеддинга запроса: {e}", exc_info=True)
            return [0.0] * 1024


query_service = QueryService()
