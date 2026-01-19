from pathlib import Path

from src.logging.logger import logger
from src.processors.document import DocumentProcessor


class IndexerService:
    """Сервис индексации документов."""

    def __init__(self):
        self.document_processor: DocumentProcessor = DocumentProcessor()

    async def index(self, path: Path, document_uuid: str = None):
        """Индексация файла."""

        try:
            suffix = path.suffix.lower()

            if suffix in self.document_processor.document_formats:
                return self.document_processor.process_file(suffix, path, document_uuid)

            else:
                logger.error("Неизвестный формат документа.")
                return []

        except Exception as e:
            logger.error(f"Ошибка при индексации файла {path}: {e}")
            return []
