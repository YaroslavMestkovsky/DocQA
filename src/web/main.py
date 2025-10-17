"""ASGI entrypoint for the DocQA FastAPI application.

Point your ASGI server to `src.web.main:app` or `src.web.app:app`.
"""

from src.web.app import app  # noqa: F401
