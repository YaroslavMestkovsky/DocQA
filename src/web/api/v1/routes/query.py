from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.services.query import query_service
from src.services.ollama import OllamaService


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


@router.post("/", response_model=QueryResponse, summary="Query RAG pipeline")
async def query_rag(request: QueryRequest) -> QueryResponse:
    # Получение эмбеддингов с использованием query_service
    response = await query_service.search(
        query=request.question,
        limit=request.top_k,
    )

    # Формирование контекста из результатов поиска
    context = "\n".join([result.texts for result in response.results if result.texts])

    # Получение ответа от LLM-модели
    llm_response = await OllamaService.ask_model(query=request.question, context=context)

    # Формирование списка пассажей
    passages = []

    for idx, result in enumerate(response.results):
        if result.texts:
            passages.append(
                Passage(
                    id=f"p{idx}",
                    text=result.texts,
                    score=result.score,
                    metadata={"source": result.file_paths[0] if result.file_paths else "unknown"}
                ),
            )

    return QueryResponse(
        answer=llm_response.get("response", "No answer from LLM."),
        passages=passages,
    )
