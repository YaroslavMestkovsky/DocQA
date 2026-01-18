from dataclasses import dataclass
from typing import List

from src.web.models.enums import FileType


@dataclass
class SearchResult:
    """Результат поиска."""
    ids: list
    chunks: list
    file_paths: list
    file_types: List[FileType]
    texts: str
    score: float

@dataclass
class SearchResponse:
    """Ответ на поисковый запрос."""
    query: str
    results: List[SearchResult]
    total_found: int
    processing_time: float
    query_embedding: List[float]
