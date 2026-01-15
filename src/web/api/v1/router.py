from fastapi import APIRouter

from src.web.api.v1.routes import (
    health,
    meta,
    query,
    qdrant,
    ollama,
    embedding,
    documents,
)


v1_router = APIRouter()

v1_router.include_router(meta.router, tags=["meta"])
v1_router.include_router(health.router, tags=["health"])
v1_router.include_router(qdrant.router, prefix="/qdrant", tags=["qdrant"])
v1_router.include_router(ollama.router, prefix="/ollama", tags=["ollama"])
v1_router.include_router(embedding.router, prefix="/embedding", tags=["embedding"])
v1_router.include_router(documents.router, prefix="/documents", tags=["documents"])
v1_router.include_router(query.router, prefix="/query", tags=["query"])
