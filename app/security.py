# app/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from .settings import settings

# Argon2 only (modern KDF, no 72-byte limit)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def _encode_jwt(sub: str, role: str, typ: str, expires_delta: timedelta) -> str:
    now = datetime.now(tz=timezone.utc)
    payload: Dict[str, Any] = {
        "sub": sub,
        "role": role,
        "typ": typ,       # "access" | "refresh"
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def create_access_token(sub: str, role: str) -> str:
    return _encode_jwt(sub, role, "access", timedelta(minutes=settings.access_token_expire_minutes))

def create_refresh_token(sub: str, role: str) -> str:
    return _encode_jwt(sub, role, "refresh", timedelta(days=settings.refresh_token_expire_days))

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None