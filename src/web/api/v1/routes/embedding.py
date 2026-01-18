from fastapi import APIRouter, HTTPException
from src.helpers.models_management import (
    check_embedding_model,
    get_embedding_model,
)
from src.services.query import query_service
from src.web.models.query_models import SearchResponseModel, SearchRequest

router = APIRouter()


@router.get("/check_models", summary="Check if all embedding models from config uploaded")
def check_models_exists() -> dict:
    return {"embedding_status": check_embedding_model()}


@router.post("/pull_model", summary="Pull embedding model")
def pull_model() -> dict:
    get_embedding_model()

    return {"success": True}

@router.post("/search", response_model=SearchResponseModel, summary="Embeddings search by request")
async def search(request: SearchRequest):
    """API для поиска."""
    try:
        # Преобразование типов файлов
        file_types = None

        if request.file_types:
            ...
            # file_types = [FileType(ft) for ft in request.file_types if ft in [t.value for t in FileType]]

        # Выполнение поиска
        response = query_service.search(
            query=request.query,
            file_types=file_types,
            limit=request.limit or 1,
            score_threshold=request.score_threshold,
        )

        # Преобразование результатов
        results = []

        for result in response.results:
            results.append({
                "ids": result.ids,
                "chunks": result.chunks,
                "file_paths": result.file_paths,
                "file_types": [file_type.value for file_type in result.file_types],
                "texts": result.texts,
                "score": result.score,
            })

        return SearchResponseModel(
            query=response.query,
            results=results,
            total_found=response.total_found,
            processing_time=response.processing_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))