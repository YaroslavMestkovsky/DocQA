"""Web application package for the DocQA project."""

# Expose the FastAPI app instance at package level for ASGI servers
from src.web.app import app  # noqa: F401
