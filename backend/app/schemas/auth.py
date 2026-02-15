"""
Pydantic schemas for authentication endpoints.
"""
from typing import Optional

from pydantic import BaseModel


class AuthUserResponse(BaseModel):
    """Authenticated user response."""

    id: str
    email: Optional[str] = None
    role: Optional[str] = None
