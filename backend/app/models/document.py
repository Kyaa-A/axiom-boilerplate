"""
Document model for storing structured data.
Separate from vector embeddings stored in Weaviate.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class Document(Base):
    """
    Document model for PostgreSQL.

    Note: This stores structured metadata.
    Embeddings are stored separately in Weaviate.
    """

    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    vector_id = Column(String(255), nullable=True, index=True)  # Reference to Weaviate vector
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title})>"
