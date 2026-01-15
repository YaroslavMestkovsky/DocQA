from fastapi import APIRouter


router = APIRouter()


@router.get("/info", summary="Get API metadata")
def get_meta_info() -> dict:
    return {
        "name": "DocQA Web API",
        "version": "0.1.0",
        "description": "FastAPI interface for DocQA RAG services",
    }


