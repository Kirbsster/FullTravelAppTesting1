from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from ..database import get_session
from ..models import User
from ..schemas import LoginIn, RegisterIn, TokenPair, UserOut
from ..security import verify_password, hash_password, create_access_token, create_refresh_token, decode_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: RegisterIn, session: Session = Depends(get_session)):
    user = User(email=payload.email, hashed_password=hash_password(payload.password), role="user", is_active=True)
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        session.rollback()
        logger.exception("Unexpected error during register")
        raise HTTPException(status_code=500, detail="Registration failed")
    session.refresh(user)
    return user

@router.post("/login", response_model=TokenPair)
def login(payload: LoginIn, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access = create_access_token(user.email, user.role)
    refresh = create_refresh_token(user.email, user.role)
    return TokenPair(access_token=access, refresh_token=refresh)

@router.post("/guest", response_model=TokenPair, status_code=201)
def guest_login(session: Session = Depends(get_session)):
    """
    Creates (or reuses) a guest user record with a random email-like label.
    Guests have role='guest' and no password; tokens are short-lived via .env settings.
    Frontend can call this to "Continue as guest".
    """
    # reuse a single guest user row for simplicity (email acts as subject)
    email = "guest@local"
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(email=email, hashed_password=None, role="guest", is_active=True)
        session.add(user); session.commit(); session.refresh(user)

    access = create_access_token(user.email, user.role)
    refresh = create_refresh_token(user.email, user.role)
    return TokenPair(access_token=access, refresh_token=refresh)

@router.post("/refresh", response_model=TokenPair)
def refresh_token(refresh_token: str):
    """
    Exchange a valid refresh token for a new access+refresh pair.
    Client stores refresh token (e.g., HttpOnly cookie) and posts it here when access expires.
    """
    data = decode_token(refresh_token)
    if not data or data.get("typ") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    email = data.get("sub")
    role = data.get("role") or "user"
    return TokenPair(
        access_token=create_access_token(email, role),
        refresh_token=create_refresh_token(email, role),
    )

@router.post("/token")
def oauth2_token(form: OAuth2PasswordRequestForm = Depends(),
                 session: Session = Depends(get_session)):
    """
    OAuth2 Password flow endpoint for Swagger/clients.
    Accepts form fields: username, password (client_id/secret ignored).
    Returns only an ACCESS token, as required by OAuth2 spec for this flow.
    """
    # In our system, "username" = email
    user = session.exec(select(User).where(User.email == form.username)).first()
    if not user or not user.hashed_password or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    # (Optionally check form.scopes here if you implement scopes)
    access = create_access_token(user.email, user.role)
    return {"access_token": access, "token_type": "bearer"}