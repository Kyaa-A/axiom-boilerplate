"""
Pydantic schemas for authentication endpoints.
"""
from typing import Optional

from pydantic import BaseModel, Field


class AuthUserResponse(BaseModel):
    """Authenticated user response."""

    id: str
    email: Optional[str] = None
    role: Optional[str] = None
    roles: list[str] = Field(default_factory=list)
    is_admin: bool = False
