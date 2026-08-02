from fastapi import FastAPI

from app.routes import database_router, health_router
from app.config.logging_config import configure_logging
from app.config.settings import get_settings
from app.routes import auth_router, database_router, health_router


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        debug=settings.debug,
    )

    app.include_router(health_router, prefix="/api")
    app.include_router(database_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")

    return app


app = create_app()
