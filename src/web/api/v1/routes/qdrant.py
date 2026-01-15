from fastapi import APIRouter
from src.helpers.qdrant_management import create_collections, check_collections as check_qdrant_collections

router = APIRouter()


@router.get("/check_collections", summary="Check if all collections from config exist")
def check_collections() -> dict:
    return {"collections_status": check_qdrant_collections()}


@router.get("/create_collections", summary="Create collections that are missing")
def create_all() -> dict:
    return create_collections()
