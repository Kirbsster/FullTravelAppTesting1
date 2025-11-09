from typing import Optional
from pydantic import BaseModel, EmailStr, constr

# ---- Auth payloads
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: str
    role: str
    typ: str   # "access" | "refresh"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class RegisterIn(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=256)  # tweak as you like

# ---- Users
class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True