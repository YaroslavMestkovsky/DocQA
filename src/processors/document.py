import uuid
import re
import hashlib
import time
import pdfplumber

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
            qdrant_manager.client.upsert(
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
        self.embedding_cache: Dict[str, List[float]] = {}
        self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()

    def process_file(self, suffix, path):
        """Обработка документа."""

        point_ids = []

        try:
            logger.debug(f"Обработка документа: {path}")
            # Извлечение текста
            extractor = self.document_formats[suffix]
            text = extractor(path)

            # Разбиение на чанки с перекрытием
            chunks = self._chunk_text(text, overlap=100)

            # Фильтруем пустые чанки
            non_empty_chunks = [chunk for chunk in chunks if chunk.strip()]

            # Создаем эмбеддинги пакетом
            embeddings = self._create_embeddings_batch(non_empty_chunks)

            with tqdm(total=len(chunks), desc="Создание эмбедингов") as pbar:
                # Обработка каждого чанка
                embedding_index = 0

                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        pbar.update(1)
                        continue

                    # Получаем эмбеддинг из пакета
                    embedding = embeddings[embedding_index]
                    embedding_index += 1

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
                    point_ids.append(point.id)
                    self._add_to_buffer(point)
                    pbar.update(1)

            self.finalize()
            logger.debug(f"Документ обработан: {path} ({len(chunks)} чанков)")

            return point_ids

        except:
            return point_ids

    def _chunk_text(self, text, chunk_size=None, overlap=50):
        """Разбиение текста на чанки с перекрытием."""
        
        if chunk_size is None:
            chunk_size = qdrant_config.processing.chunk_size
        
        # Разбиваем текст на предложения
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Если предложение слишком большое, разбиваем его
            if sentence_length > chunk_size:
                # Разбиваем большое предложение на части
                words = sentence.split()

                for word in words:
                    if current_length + len(word) + 1 > chunk_size and current_chunk:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = [word]
                        current_length = len(word)
                    else:
                        current_chunk.append(word)
                        current_length += len(word) + 1
                
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0
            
            # Обычная обработка предложения
            elif current_length + sentence_length + 1 > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                # Добавляем перекрытие: берем последние overlap символов из предыдущего чанка

                if overlap > 0 and len(chunks) > 0:
                    last_chunk = chunks[-1]
                    overlap_text = last_chunk[-overlap:] if len(last_chunk) > overlap else last_chunk
                    current_chunk = [overlap_text, sentence]
                    current_length = len(overlap_text) + len(sentence) + 1
                else:
                    current_chunk = [sentence]
                    current_length = len(sentence)
            else:
                current_chunk.append(sentence)
                current_length += len(sentence) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _create_embedding(self, text: str) -> List[float]:
        """Создание эмбеддинга для текста с кэшированием."""

        try:
            if not text.strip():
                return [0.0] * self.embedding_dimension  # Пустой вектор

            # Создаем хеш текста для кэширования
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            
            # Проверяем кэш
            if text_hash in self.embedding_cache:
                return self.embedding_cache[text_hash]

            embedding = self.embedding_model.encode(text, show_progress_bar=False)
            embedding_list = embedding.tolist()
            
            # Сохраняем в кэш
            self.embedding_cache[text_hash] = embedding_list
            
            return embedding_list

        except Exception as e:
            logger.error(f"Ошибка при создании эмбеддинга: {e}", exc_info=True)
            return [0.0] * self.embedding_dimension

    def _create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Создание эмбеддингов для пакета текстов."""
        
        if not texts:
            return []
        
        # Фильтруем пустые тексты
        non_empty_texts = [text for text in texts if text.strip()]
        
        if not non_empty_texts:
            return [[0.0] * self.embedding_dimension] * len(texts)
        
        try:
            # Создаем эмбеддинги для пакета
            embeddings = self.embedding_model.encode(non_empty_texts, show_progress_bar=False)
            
            # Преобразуем в список списков
            embeddings_list = embeddings.tolist()
            
            # Добавляем пустые векторы для пустых текстов
            result = []
            text_index = 0
            for text in texts:
                if text.strip():
                    result.append(embeddings_list[text_index])
                    text_index += 1
                else:
                    result.append([0.0] * self.embedding_dimension)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при создании эмбеддингов для пакета: {e}", exc_info=True)
            return [[0.0] * self.embedding_dimension] * len(texts)

    def _normalize_text(self, text: str) -> str:
        """Нормализация текста: удаление лишних пробелов, нормализация переносов и т.д."""
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        # Нормализуем переносы строк
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Удаляем лишние пробелы в начале и конце
        text = text.strip()

        return text

    def _extract_pdf_text(self, path):
        """Извлечение текста из PDF файла с использованием pdfplumber."""

        result = ""

        try:
            text_parts = []

            with pdfplumber.open(path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()

                        if page_text and page_text.strip():
                            # Нормализация текста
                            normalized_text = self._normalize_text(page_text)
                            text_parts.append(normalized_text)

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
