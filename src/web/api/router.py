from fastapi import APIRouter

from src.web.api.v1.router import v1_router


api_router = APIRouter()

# Versioned APIs
api_router.include_router(v1_router, prefix="/v1")
