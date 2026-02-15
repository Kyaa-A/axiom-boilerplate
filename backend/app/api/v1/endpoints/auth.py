"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends

from app.core.auth import AuthUser, get_current_user
from app.schemas.auth import AuthUserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=AuthUserResponse)
async def get_me(current_user: AuthUser = Depends(get_current_user)):
    """Return the authenticated user."""
    return AuthUserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
    )
