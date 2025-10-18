from fastapi import APIRouter
from src.helpers.health_checks import create_health_report

router = APIRouter()


@router.get("/health", summary="Health check")
def health_check() -> dict:
    return create_health_report()
