from fastapi import FastAPI

from src.web.api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(title="DocQA Web API", version="0.1.0")
    app.include_router(api_router)

    return app


# ASGI entrypoint
app = create_app()
