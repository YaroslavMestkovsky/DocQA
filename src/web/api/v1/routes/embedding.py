from fastapi import APIRouter
from src.helpers.models_management import (
    check_embedding_model,
)


router = APIRouter(prefix="/ollama")


@router.get("/check_models", summary="Check if all embedding models from config uploaded")
def check_models_exists() -> dict:
    return {"missing_models": check_embedding_model()}
