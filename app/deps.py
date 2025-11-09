from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from .database import get_session
from .models import User
from .security import decode_token

# OAuth2 “password” flow – Swagger will show username/password fields
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")  # <= new form endpoint below

def get_current_user(token: str = Depends(oauth2_scheme),
                     session: Session = Depends(get_session)) -> User:
    data = decode_token(token)
    if not data or data.get("typ") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = session.exec(select(User).where(User.email == data["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or unknown user")
    return user