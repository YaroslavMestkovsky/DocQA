from fastapi import APIRouter
from src.helpers.health_checks import create_health_report

router = APIRouter()


@router.get("/health", summary="Health check")
async def health_check() -> dict:
    return await create_health_report()
