from fastapi import APIRouter
from src.helpers.models_management import (
    check_embedding_model,
    pull_embedding_model,
)


router = APIRouter(prefix="/ollama")


@router.get("/check_models", summary="Check if all embedding models from config uploaded")
def check_models_exists() -> dict:
    return {"missing_models": check_embedding_model()}


@router.get("/pull_embedding_model", summary="Pulls embedding models from config")
def pull_model() -> dict:
    return pull_embedding_model()

