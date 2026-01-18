from typing import List, Optional, Dict, Any
from pathlib import Path
import tempfile
import uuid

from fastapi import APIRouter, UploadFile, File, Query
from pydantic import BaseModel

from src.services.indexer import IndexerService


router = APIRouter()


class DocumentMetadata(BaseModel):
    source: Optional[str] = None
    tags: Optional[List[str]] = None


class IngestResponse(BaseModel):
    document_ids: List[str]
    performance: Optional[Dict[str, Any]] = None


class DeleteResponse(BaseModel):
    deleted_ids: List[str]


@router.post("/ingest", response_model=IngestResponse, summary="Ingest documents")
async def ingest_documents(
    files: List[UploadFile] = File(..., description="Files to ingest"),
) -> IngestResponse:
    """Обработка загруженных документов и создание эмбеддингов."""
    
    indexer = IndexerService()
    document_ids = []
    performance_stats = {
        "total_files": 0,
        "processed_files": 0,
        "total_points": 0,
    }
    
    # Создаем временную директорию для сохранения файлов
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        for upload_file in files:
            performance_stats["total_files"] += 1
            
            # Проверяем, что файл является PDF todo в будущем открыть другие типы
            if not upload_file.filename.lower().endswith('.pdf'):
                continue
            
            # Сохраняем файл во временную директорию
            file_path = temp_path / upload_file.filename
            with open(file_path, "wb") as buffer:
                content = await upload_file.read()
                buffer.write(content)
            
            # Обрабатываем файл
            try:
                point_ids = indexer.index(file_path)
                # Добавляем все ID точек для этого документа
                document_ids.extend(point_ids)
                performance_stats["processed_files"] += 1
                performance_stats["total_points"] += len(point_ids)
            except Exception as e:
                # Логируем ошибку и продолжаем обработку следующих файлов todo
                continue
    
    return IngestResponse(
        document_ids=document_ids,
        performance=performance_stats,
    )


@router.get("/", summary="List documents (stub)")
def list_documents(
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)
) -> dict:
    return {"items": [], "limit": limit, "offset": offset}


@router.delete("/", response_model=DeleteResponse, summary="Delete documents by IDs (stub)")
def delete_documents(ids: List[str] = Query(..., description="IDs to delete")) -> DeleteResponse:
    return DeleteResponse(deleted_ids=ids)
