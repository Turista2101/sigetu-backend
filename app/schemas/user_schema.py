from typing import Annotated, Literal
from datetime import datetime
from pydantic import BaseModel, EmailStr, StringConstraints

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Annotated[str, StringConstraints(min_length=3, max_length=50, strip_whitespace=True)]
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]
    programa_academico: Literal["ingenierias", "derecho", "finanzas"] | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    programa_academico: Literal["ingenierias", "derecho", "finanzas"] | None
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"