"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends

from app.core.auth import AuthUser, get_current_user
from app.core.rate_limit import auth_rate_limit
from app.schemas.auth import AuthUserResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[Depends(auth_rate_limit)],
)


@router.get("/me", response_model=AuthUserResponse)
async def get_me(current_user: AuthUser = Depends(get_current_user)):
    """Return the authenticated user."""
    return AuthUserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        roles=sorted(current_user.roles),
        is_admin=current_user.is_admin,
    )
