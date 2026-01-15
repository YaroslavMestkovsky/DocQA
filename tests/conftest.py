"""Фикстуры для тестирования."""

import pytest

from fastapi.testclient import TestClient
from src.web.app import create_app


@pytest.fixture(scope="module")
def client():
    """Создает тестовый клиент для FastAPI."""
    app = create_app()

    with TestClient(app) as client:
        yield client
