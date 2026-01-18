from typing import List, Dict, Any, Optional
from pydantic import BaseModel


# Pydantic модели для API
class SearchRequest(BaseModel):
    query: str
    file_types: Optional[List[str]] = None
    limit: int = 1
    score_threshold: float = 0.7


class SearchResponseModel(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_found: int
    processing_time: float
