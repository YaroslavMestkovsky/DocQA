from typing import List, Optional, Dict, Any
from pathlib import Path
import tempfile
import uuid

from fastapi import APIRouter, UploadFile, File, Query
from pydantic import BaseModel

from src.managers.qdrant import qdrant_manager
from src.helpers.configs_hub import qdrant_config
from src.services.indexer import IndexerService


router = APIRouter()


class DocumentMetadata(BaseModel):
    source: Optional[str] = None
    tags: Optional[List[str]] = None


class IngestResponse(BaseModel):
    document_ids: List[str]
    document_uuid: str
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
            
            # Генерируем уникальный идентификатор для документа
            document_uuid = str(uuid.uuid4())
            
            # Обрабатываем файл
            try:
                point_ids = await indexer.index(file_path, document_uuid)
                # Добавляем все ID точек для этого документа
                document_ids.extend(point_ids)
                performance_stats["processed_files"] += 1
                performance_stats["total_points"] += len(point_ids)
            except Exception as e:
                # Логируем ошибку и продолжаем обработку следующих файлов todo
                continue
    
    return IngestResponse(
        document_ids=document_ids,
        document_uuid=document_uuid,
        performance=performance_stats,
    )


@router.get("/", summary="List documents")
async def list_documents(
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)
) -> dict:
    """Получение списка документов из Qdrant."""

    collection_name = qdrant_config.defaults.default_collection

    # Получаем все точки из коллекции
    points = qdrant_manager.client.scroll(
        collection_name=collection_name,
        limit=limit,
        offset=offset,
        with_payload=True,
        with_vectors=False,
    )

    # Формируем список документов
    items = []

    for point in points[0]:
        payload = point.payload
        info = { # todo как-то тупо выглядит
            "document": point.payload['file_path'].split('/')[-1],
            "document_uuid": payload['document_uuid'],
        }

        if info in items:
            continue
        else:
            items.append(info)

    return {"items": items, "limit": limit, "offset": offset}


@router.delete("/", response_model=DeleteResponse, summary="Delete documents by UUID")
async def delete_documents(document_uuid: str = Query(..., description="Document UUID to delete all related points")) -> DeleteResponse:
    """Удаление всех точек, связанных с конкретным документом по UUID."""

    from qdrant_client.models import Filter, FieldCondition, MatchValue

    collection_name = qdrant_config.defaults.default_collection

    # Находим все точки, связанные с данным UUID
    points = qdrant_manager.client.scroll(
        collection_name=collection_name,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="document_uuid",
                    match=MatchValue(value=document_uuid),
                ),
            ],
        ),
        with_payload=False,
        limit=10000,  # Большой лимит, чтобы получить все точки
    )

    # Получаем ID точек для удаления
    points_to_delete = [point.id for point in points[0]]

    # Удаляем точки из коллекции
    if points_to_delete:
        qdrant_manager.client.delete(
            collection_name=collection_name,
            points_selector=points_to_delete,
        )

    return DeleteResponse(deleted_ids=points_to_delete)
