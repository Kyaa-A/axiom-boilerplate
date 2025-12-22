"""
Pydantic schemas for document API requests and responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document schema."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    source: Optional[str] = Field(None, max_length=255)


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""

    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    source: Optional[str] = Field(None, max_length=255)


class DocumentResponse(DocumentBase):
    """Schema for document responses."""

    id: UUID
    vector_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    """Schema for RAG query requests."""

    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    """Schema for RAG query responses."""

    query: str
    response: str
    sources: list[dict]
