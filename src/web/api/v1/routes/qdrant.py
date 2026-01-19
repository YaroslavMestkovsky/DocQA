from fastapi import APIRouter
from src.helpers.qdrant_management import create_collections, check_collections as check_qdrant_collections

router = APIRouter()


@router.get("/check_collections", summary="Check if all collections from config exist")
async def check_collections() -> dict:
    return {"collections_status": await check_qdrant_collections()}


@router.get("/create_collections", summary="Create collections that are missing")
async def create_all() -> dict:
    return await create_collections()
