from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import ALGORITHM, SECRET_KEY


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise credentials_exception from exc

    sub = payload.get("sub")
    role = payload.get("role")
    if not sub or not role:
        raise credentials_exception

    return payload


def require_student_role(payload: dict = Depends(get_current_token_payload)) -> dict:
    if payload.get("role") != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo estudiantes pueden agendar citas",
        )
    return payload


def require_secretaria_role(payload: dict = Depends(get_current_token_payload)) -> dict:
    if payload.get("role") != "secretaria":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo secretaría puede consultar la cola",
        )
    return payload


def require_secretaria_or_admin_role(payload: dict = Depends(get_current_token_payload)) -> dict:
    if payload.get("role") not in {"secretaria", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo secretaría o admin pueden actualizar estados",
        )
    return payload
