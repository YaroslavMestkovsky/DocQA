from fastapi import APIRouter, Query
from src.helpers.ollama_management import (
    get_models,
    pull_model,
    check_models,
)


router = APIRouter(prefix="/ollama")


@router.get("/get_models_list", summary="Get all ollama models")
def get_all() -> dict:
    return get_models()


@router.get("/check_models", summary="Check if all models from config uploaded")
def check_models_exists() -> dict:
    return {"missing_models": check_models()}


@router.post("/pull_model", summary="Pull ollama model by name")
def pull_model_by_name(name: str = Query(..., description="Model name to pull")) -> dict:
    return pull_model(name)
