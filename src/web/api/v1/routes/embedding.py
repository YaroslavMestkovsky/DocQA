from fastapi import APIRouter
from src.helpers.models_management import (
    check_embedding_model, get_embedding_model,
)


router = APIRouter()


@router.get("/check_models", summary="Check if all embedding models from config uploaded")
def check_models_exists() -> dict:
    return {"embedding_status": check_embedding_model()}


@router.post("/pull_model", summary="Pull embedding model")
def pull_model() -> dict:
    get_embedding_model()

    return {"success": True}


@router.post("/get_embeddings_from_qdrant")
def get_embeddings_from_qdrant() -> dict:
    ...
