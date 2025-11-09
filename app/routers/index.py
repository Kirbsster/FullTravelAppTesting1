from fastapi import APIRouter, Depends
from ..deps import get_current_user
from ..models import User

router = APIRouter(tags=["app"])

@router.get("/index")
def index(current_user: User = Depends(get_current_user)):
    # This is your “post-login landing” payload. Frontend can call after auth.
    return {
        "message": "Welcome to the Bike Suspension Viz backend!",
        "user": {"email": current_user.email, "role": current_user.role}
    }

@router.get("/users/me")
def whoami(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role, "is_active": current_user.is_active}