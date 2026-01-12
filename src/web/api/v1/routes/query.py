from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter()


class QueryRequest(BaseModel):
    question: str = Field(..., description="User question to query over the knowledge base")
    top_k: int = Field(5, ge=1, le=50, description="Number of candidate passages to retrieve")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata filters")


class Passage(BaseModel):
    id: str
    text: str
    score: float
    metadata: Dict[str, Any] = {}


class QueryResponse(BaseModel):
    answer: str
    passages: List[Passage] = []


@router.post("/", response_model=QueryResponse, summary="Query RAG pipeline (stub)")
def query_rag(request: QueryRequest) -> QueryResponse:
    # Placeholder implementation; integrate with processors/services later
    dummy_passages = [
        Passage(id="p1", text="Example passage text.", score=0.9, metadata={"source": "stub"})
    ]
    return QueryResponse(answer="This is a stub answer.", passages=dummy_passages)
