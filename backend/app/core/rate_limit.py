"""
Redis-backed API rate limiting dependencies.
"""
from __future__ import annotations

import time
from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from app.core.auth import AuthUser, get_current_user
from app.core.cache import cache_client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _resolve_identifier(request: Request, current_user: Optional[AuthUser]) -> str:
    """
    Resolve a stable identifier for rate limiting.
    Prefer authenticated user ID; fallback to client IP.
    """
    if current_user:
        return current_user.id

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        first_ip = forwarded_for.split(",")[0].strip()
        if first_ip:
            return first_ip

    client_host = request.client.host if request.client else "unknown"
    return client_host


def _rate_limit_key(scope: str, identifier: str, window_seconds: int) -> str:
    """Build Redis key scoped to a fixed time window."""
    bucket = int(time.time()) // window_seconds
    return f"rl:{scope}:{identifier}:{bucket}"


async def enforce_rate_limit(
    *,
    request: Request,
    scope: str,
    requests_per_window: int,
    window_seconds: int,
    current_user: Optional[AuthUser],
) -> None:
    """Enforce a fixed-window Redis rate limit."""
    if not settings.RATE_LIMIT_ENABLED:
        return

    if requests_per_window <= 0 or window_seconds <= 0:
        return

    identifier = _resolve_identifier(request, current_user)
    key = _rate_limit_key(scope, identifier, window_seconds)
    count = await cache_client.increment_with_expiry(
        key=key,
        expire_seconds=window_seconds,
    )

    if count <= requests_per_window:
        return

    retry_after = await cache_client.ttl(key)
    retry_after_seconds = max(retry_after, 1)

    logger.warning(
        "Rate limit exceeded",
        scope=scope,
        identifier=identifier,
        requests_per_window=requests_per_window,
        window_seconds=window_seconds,
        current_count=count,
    )

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded. Please retry later.",
        headers={"Retry-After": str(retry_after_seconds)},
    )


def build_rate_limit_dependency(
    *,
    scope: str,
    requests_per_window: int,
    window_seconds: int,
):
    """Build a FastAPI dependency enforcing the supplied rate limit."""

    async def dependency(
        request: Request,
        current_user: AuthUser = Depends(get_current_user),
    ) -> None:
        await enforce_rate_limit(
            request=request,
            scope=scope,
            requests_per_window=requests_per_window,
            window_seconds=window_seconds,
            current_user=current_user,
        )

    return dependency


auth_rate_limit = build_rate_limit_dependency(
    scope="auth",
    requests_per_window=settings.RATE_LIMIT_AUTH_REQUESTS_PER_WINDOW,
    window_seconds=settings.RATE_LIMIT_AUTH_WINDOW_SECONDS,
)

ai_rate_limit = build_rate_limit_dependency(
    scope="ai",
    requests_per_window=settings.RATE_LIMIT_AI_REQUESTS_PER_WINDOW,
    window_seconds=settings.RATE_LIMIT_AI_WINDOW_SECONDS,
)

documents_rate_limit = build_rate_limit_dependency(
    scope="documents",
    requests_per_window=settings.RATE_LIMIT_DOCUMENTS_REQUESTS_PER_WINDOW,
    window_seconds=settings.RATE_LIMIT_DOCUMENTS_WINDOW_SECONDS,
)
