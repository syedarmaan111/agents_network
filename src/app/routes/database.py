from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.session import get_db


router = APIRouter(
    prefix="/database",
    tags=["database"],
)


@router.get("/health")
def database_health(
    database: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        database.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "postgresql",
        }
    except SQLAlchemyError as error:
        print("DATABASE ERROR:", error)

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": True, "message": str(error)},
        )
