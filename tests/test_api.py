"""Тесты для основных эндпоинтов API."""


import pytest


def test_health_check(client):
    """Тест для эндпоинта health check."""
    response = client.get("/v1/health")
    assert response.status_code == 200


def test_ollama_check_models(client):
    """Тест для эндпоинта ollama check models."""
    response = client.get("/v1/ollama/check_models")
    assert response.status_code == 200


def test_embedding_check_models(client):
    """Тест для эндпоинта embedding check models."""
    response = client.get("/v1/embedding/check_models")
    assert response.status_code == 200


def test_qdrant_check_collections(client):
    """Тест для эндпоинта qdrant check collections."""
    response = client.get("/v1/qdrant/check_collections")
    assert response.status_code == 200
