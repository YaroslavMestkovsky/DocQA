from fastapi import APIRouter
from src.helpers.qdrant_management import create_collections

router = APIRouter(prefix="/qdrant")


@router.get("/create_collections", summary="Check if collections exists and create if needed")
def create_all() -> dict:
    return create_collections()
