from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserRegister
from app.utils.security import hash_password, verify_password


def get_user_by_email(
    database: Session,
    email: str,
) -> User | None:
    statement = select(User).where(User.email == email)

    return database.scalar(statement)


def register_user(
    database: Session,
    user_data: UserRegister,
) -> User:
    existing_user = get_user_by_email(
        database,
        str(user_data.email),
    )

    if existing_user is not None:
        raise ValueError("A user with this email already exists")

    user = User(
        email=str(user_data.email),
        password_hash=hash_password(user_data.password),
    )

    database.add(user)
    database.commit()
    database.refresh(user)

    return user


def authenticate_user(
    database: Session,
    email: str,
    password: str,
) -> User | None:
    user = get_user_by_email(database, email)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user