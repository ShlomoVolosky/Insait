"""Application entry point / app factory."""

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.routes import router
from app.infrastructure.config import Settings


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(title=settings.app_name, version=settings.version)
    app.include_router(router)
    register_error_handlers(app)
    return app


app = create_app()
