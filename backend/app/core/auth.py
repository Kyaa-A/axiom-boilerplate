"""
Authentication and authorization utilities.
Validates Supabase JWTs for protected API routes and normalizes role claims.
"""
from typing import Any, Dict, Optional, Set

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


class AuthUser(BaseModel):
    """Authenticated user claims extracted from JWT."""

    id: str
    email: Optional[str] = None
    role: str = "user"
    roles: Set[str] = Field(default_factory=set)
    raw_claims: Dict[str, Any]

    @property
    def is_admin(self) -> bool:
        """Return True for admin-equivalent roles."""
        return bool({"admin", "super_admin", "service_role"} & self.roles)


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


def _normalize_role_values(value: Any) -> Set[str]:
    """Normalize a role claim to a lowercase set."""
    if value is None:
        return set()

    if isinstance(value, str):
        normalized = value.strip().lower()
        return {normalized} if normalized else set()

    if isinstance(value, (list, tuple, set)):
        roles: Set[str] = set()
        for item in value:
            if isinstance(item, str):
                normalized = item.strip().lower()
                if normalized:
                    roles.add(normalized)
        return roles

    return set()


def _extract_roles(payload: Dict[str, Any]) -> Set[str]:
    """Extract roles from common JWT claim locations."""
    roles: Set[str] = set()

    roles.update(_normalize_role_values(payload.get("role")))
    roles.update(_normalize_role_values(payload.get("roles")))

    app_metadata = payload.get("app_metadata")
    if isinstance(app_metadata, dict):
        roles.update(_normalize_role_values(app_metadata.get("role")))
        roles.update(_normalize_role_values(app_metadata.get("roles")))

    user_metadata = payload.get("user_metadata")
    if isinstance(user_metadata, dict):
        roles.update(_normalize_role_values(user_metadata.get("role")))
        roles.update(_normalize_role_values(user_metadata.get("roles")))

    realm_access = payload.get("realm_access")
    if isinstance(realm_access, dict):
        roles.update(_normalize_role_values(realm_access.get("roles")))

    if not roles:
        roles.add("user")

    return roles


def _resolve_primary_role(roles: Set[str]) -> str:
    """Resolve a stable primary role for response payloads."""
    if "admin" in roles or "super_admin" in roles:
        return "admin"
    if "service_role" in roles:
        return "service_role"
    if "authenticated" in roles or "user" in roles:
        return "user"
    return sorted(roles)[0]


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

    roles = _extract_roles(payload)

    return AuthUser(
        id=user_id,
        email=payload.get("email"),
        role=_resolve_primary_role(roles),
        roles=roles,
        raw_claims=payload,
    )


async def require_admin(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Ensure the current user has an admin role."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
