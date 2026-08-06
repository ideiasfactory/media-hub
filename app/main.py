"""Composition root — keep `uvicorn app.main:app` as the process entrypoint."""

from bff.app import create_app

app = create_app()
