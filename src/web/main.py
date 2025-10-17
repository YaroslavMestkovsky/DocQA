"""Development entrypoint for running the FastAPI app with uvicorn.

This module is optional; production should use an ASGI server pointing to
`src.web:app` or `src.web.app:app`.
"""

import uvicorn

from .app import app


def run() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()


