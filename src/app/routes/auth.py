from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import RevokedToken
from app.schemas import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth import authenticate_user, register_user
from app.utils.security import create_access_token, login_required


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

bearer_scheme = HTTPBearer(auto_error=False)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    database: Session = Depends(get_db),
) -> UserResponse:
    try:
        return register_user(database, user_data)
    except ValueError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": True, "message": "User already exists"},
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: UserLogin,
    database: Session = Depends(get_db),
) -> TokenResponse:
    user = authenticate_user(
        database,
        str(login_data.email),
        login_data.password,
    )

    if user is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": True, "message": "Invalid email or password"},
        )

    access_token = create_access_token(
        subject=str(user.id),
    )

    return TokenResponse(
        access_token=access_token,
    )

@router.post("/logout", dependencies=[Depends(bearer_scheme)])
@login_required
def logout(
    request: Request,
    database: Session = Depends(get_db),
):
    token = request.headers["Authorization"].removeprefix("Bearer ")

    database.add(RevokedToken(token=token))
    database.commit()

    return {
        "error": False,
        "message": "Logout successful",
    }
