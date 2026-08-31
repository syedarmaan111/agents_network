from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any

import jwt
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.models import RevokedToken


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    return password_hasher.verify(
        plain_password,
        password_hash,
    )


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()

    expires_at = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(
            minutes=settings.access_token_expire_minutes,
        )
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        request: Request = kwargs["request"]
        database: Session = kwargs["database"]
        authorization = request.headers.get("Authorization", "")

        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": True, "message": "Authentication token is required"},
            )

        token = authorization.removeprefix("Bearer ")
        settings = get_settings()

        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except jwt.PyJWTError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": True, "message": "Invalid or expired token"},
            )

        try:
            request.state.user_id = int(payload["sub"])
        except (KeyError, TypeError, ValueError):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": True, "message": "Invalid or expired token"},
            )

        revoked_token = database.scalar(
            select(RevokedToken).where(RevokedToken.token == token)
        )
        if revoked_token is not None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": True, "message": "Token has been revoked"},
            )

        return function(*args, **kwargs)

    return wrapper
