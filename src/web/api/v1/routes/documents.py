from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Query
from pydantic import BaseModel


router = APIRouter()


class DocumentMetadata(BaseModel):
    source: Optional[str] = None
    tags: Optional[List[str]] = None


class IngestResponse(BaseModel):
    document_ids: List[str]


class DeleteResponse(BaseModel):
    deleted_ids: List[str]


@router.post("/ingest", response_model=IngestResponse, summary="Ingest documents")
async def ingest_documents(
    files: List[UploadFile] = File(..., description="Files to ingest"),
) -> IngestResponse:
    # Placeholder: return dummy IDs
    ids = [f"doc_{i}" for i, _ in enumerate(files, start=1)]
    return IngestResponse(document_ids=ids)


@router.get("/", summary="List documents (stub)")
def list_documents(
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)
) -> dict:
    return {"items": [], "limit": limit, "offset": offset}


@router.delete("/", response_model=DeleteResponse, summary="Delete documents by IDs")
def delete_documents(ids: List[str] = Query(..., description="IDs to delete")) -> DeleteResponse:
    return DeleteResponse(deleted_ids=ids)


