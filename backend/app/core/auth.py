"""
Authentication and authorization utilities.
Validates Supabase JWTs for protected API routes.
"""
from typing import Optional, Dict, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


class AuthUser(BaseModel):
    """Authenticated user claims extracted from JWT."""

    id: str
    email: Optional[str] = None
    role: Optional[str] = None
    raw_claims: Dict[str, Any]


def _unauthorized(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decode_access_token(token: str) -> Dict[str, Any]:
    decode_kwargs: Dict[str, Any] = {
        "algorithms": [settings.SUPABASE_JWT_ALGORITHM],
    }

    if settings.SUPABASE_JWT_AUDIENCE:
        decode_kwargs["audience"] = settings.SUPABASE_JWT_AUDIENCE
    else:
        decode_kwargs["options"] = {"verify_aud": False}

    return jwt.decode(
        token,
        settings.SUPABASE_JWT_SECRET,
        **decode_kwargs,
    )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> AuthUser:
    """
    Validate Bearer token and return authenticated user claims.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    token = credentials.credentials

    try:
        payload = _decode_access_token(token)
    except jwt.ExpiredSignatureError as e:
        logger.warning("Expired auth token", error=str(e))
        raise _unauthorized("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid auth token", error=str(e))
        raise _unauthorized("Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise _unauthorized("Invalid token payload")

    return AuthUser(
        id=user_id,
        email=payload.get("email"),
        role=payload.get("role"),
        raw_claims=payload,
    )
