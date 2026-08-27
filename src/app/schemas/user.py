from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(character.isupper() for character in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(character.islower() for character in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(character.isdigit() for character in password):
            raise ValueError("Password must contain at least one number")
        if not any(not character.isalnum() for character in password):
            raise ValueError("Password must contain at least one special character")

        return password


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
