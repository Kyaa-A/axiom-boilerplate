"""
Document repository for database operations.
Implements repository pattern for clean separation.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentRepository:
    """Repository for document database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document_data: DocumentCreate) -> Document:
        """Create a new document."""
        document = Document(**document_data.model_dump())
        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)

        logger.info("Document created", document_id=str(document.id))
        return document

    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """Get all documents with pagination."""
        result = await self.db.execute(
            select(Document).offset(skip).limit(limit).order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self, document_id: UUID, document_data: DocumentUpdate
    ) -> Optional[Document]:
        """Update a document."""
        # Get existing document
        document = await self.get_by_id(document_id)
        if not document:
            return None

        # Update fields
        update_data = document_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)

        await self.db.flush()
        await self.db.refresh(document)

        logger.info("Document updated", document_id=str(document_id))
        return document

    async def delete(self, document_id: UUID) -> bool:
        """Delete a document."""
        result = await self.db.execute(
            delete(Document).where(Document.id == document_id)
        )

        deleted = result.rowcount > 0
        if deleted:
            logger.info("Document deleted", document_id=str(document_id))

        return deleted

    async def update_vector_id(
        self, document_id: UUID, vector_id: str
    ) -> Optional[Document]:
        """Update the vector ID reference for a document."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        document.vector_id = vector_id
        await self.db.flush()
        await self.db.refresh(document)

        logger.info(
            "Document vector ID updated",
            document_id=str(document_id),
            vector_id=vector_id,
        )
        return document
