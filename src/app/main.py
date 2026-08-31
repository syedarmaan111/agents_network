import app.models  # Register all SQLAlchemy models before creating tables.
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config.logging_config import configure_logging
from app.config.settings import get_settings
from app.database.session import create_tables
from app.routes import auth_router, chat_router, database_router, health_router


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
    app.include_router(chat_router, prefix="/api")

    @app.on_event("startup")
    def initialize_database() -> None:
        create_tables()

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": True, "message": error.errors()[0]["msg"]},
        )

    return app


app = create_app()
