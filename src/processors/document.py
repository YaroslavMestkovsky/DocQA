import uuid
import PyPDF2

from tqdm import tqdm
from abc import abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer

from src.logging.logger import logger
from src.helpers.configs_hub import qdrant_config
from src.managers.qdrant import qdrant_manager
from src.helpers.models_management import get_embedding_model


class BaseProcessor:
    """Базовый процессор."""

    def __init__(self):
        self.buffer: List[PointStruct] = []
        self.processed_count: int = 0
        self.chunk_size: int = qdrant_config.processing.chunk_size
        self.batch_size = qdrant_config.processing.batch_size

    @abstractmethod
    def process_file(self, suffix: str, path: Path) -> bool:
        """Обработка одного файла."""

    def _flush_batch(self):
        """Отправка накопленного батча в Qdrant."""

        try:
            qdrant_manager.upsert(
                collection_name=qdrant_config.defaults.default_collection,
                points=self.buffer,
            )
            self.processed_count += len(self.buffer)
            logger.debug(f"Обработано {len(self.buffer)} элементов. Всего: {self.processed_count}")

        except Exception as e:
            logger.error(f"Ошибка при отправке батча: {e}", exc_info=True)
            raise
        finally:
            self.buffer = []

    def _create_point(
            self,
            vector: List[float],
            payload: Dict[str, Any],
            point_id: Optional[str] = None,
    ) -> PointStruct:
        """Создание точки для Qdrant."""

        if point_id is None:
            point_id = str(uuid.uuid4())

        return PointStruct(
            id=point_id,
            vector=vector,
            payload=payload,
        )

    def _add_to_buffer(self, point: PointStruct):
        """Добавление точки в буфер."""

        self.buffer.append(point)

        if len(self.buffer) >= self.batch_size:
            self._flush_batch()

    def finalize(self):
        """Финализация обработки - отправка оставшихся данных."""

        if self.buffer:
            self._flush_batch()

        logger.debug(f"Обработка завершена. Всего обработано: {self.processed_count}")


class DocumentProcessor(BaseProcessor):
    """Процессор для обработки документов."""

    def __init__(self):
        super().__init__()

        # Поддерживаемые форматы
        self.document_formats = {
            '.pdf': self._extract_pdf_text,
            '.docx': self._extract_docx_text,
            '.doc': self._extract_doc_text,
            # '.pptx': self._extract_pptx_text,
            # '.ppt': self._extract_ppt_text,
            '.xlsx': self._extract_xlsx_text,
            '.xls': self._extract_xls_text,
            '.html': self._extract_html_text,
            '.htm': self._extract_html_text,
            '.txt': self._extract_txt_text,
            '.md': self._extract_md_text,
            # '.rtf': self._extract_rtf_text,
        }

        self.embedding_model: SentenceTransformer = get_embedding_model()

    def process_file(self, suffix, path):
        """Обработка документа."""

        try:
            logger.debug(f"Обработка документа: {path}")
            # Извлечение текста
            extractor = self.document_formats[suffix]
            text = extractor(path)

            # Разбиение на чанки
            chunks = self._chunk_text(text)

            with tqdm(total=len(chunks), desc="Создание эмбедингов") as pbar:
                # Обработка каждого чанка
                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue

                    # Создание эмбеддинга
                    embedding = self._create_embedding(chunk)

                    # Создание точки для Qdrant
                    payload = {
                        "file_path": str(path),
                        "file_type": "document",
                        "file_format": suffix,
                        "text": chunk,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "file_size": path.stat().st_size,
                    }

                    point = self._create_point(embedding, payload)
                    self._add_to_buffer(point)
                    pbar.update(1)

            self.finalize()
            logger.debug(f"Документ обработан: {path} ({len(chunks)} чанков)")

        except:
            ...

    def _chunk_text(self, text):
        """Разбиение текста на чанки."""

        words = text.split()
        chunks = []

        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > qdrant_config.processing.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _create_embedding(self, text: str) -> List[float]:
        """Создание эмбеддинга для текста."""

        try:
            if not text.strip():
                return [0.0] * 1024  # Пустой вектор

            embedding = self.embedding_model.encode(text, show_progress_bar=False)
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Ошибка при создании эмбеддинга: {e}", exc_info=True)
            return [0.0] * 1024

    def _extract_pdf_text(self, path):
        """Извлечение текста из PDF файла."""

        result = ""

        try:
            text_parts = []

            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()

                        if page_text.strip():
                            text_parts.append(page_text)

                    except Exception as e:
                        logger.warning(f"Ошибка при извлечении текста со страницы {page_num + 1}: {e}")
                        continue

            text = "\n".join(text_parts)
            logger.debug(f"Извлечено {len(text)} символов из PDF: {path}")

            result = text

        except Exception as e:
            logger.error(f"Ошибка при извлечении текста из PDF {path}: {e}", exc_info=True)

        return result
        
    def _extract_docx_text(self, path):
        ...

    def _extract_doc_text(self, path):
        ...

    def _extract_xlsx_text(self, path):
        ...

    def _extract_xls_text(self, path):
        ...

    def _extract_html_text(self, path):
        ...

    def _extract_txt_text(self, path):
        ...

    def _extract_md_text(self, path):
        ...
