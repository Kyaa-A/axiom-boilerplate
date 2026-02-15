"""
Document repository for database operations.
Implements repository pattern for clean separation.
"""
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentRepository:
    """Repository for document database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _apply_owner_scope(statement: Any, owner_id: Optional[str]) -> Any:
        """Restrict statements to an owner when scope is provided."""
        if owner_id:
            return statement.where(Document.owner_id == owner_id)
        return statement

    async def create(self, document_data: DocumentCreate, owner_id: str) -> Document:
        """Create a new document."""
        document = Document(**document_data.model_dump(), owner_id=owner_id)
        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)

        logger.info(
            "Document created",
            document_id=str(document.id),
            owner_id=owner_id,
        )
        return document

    async def get_by_id(
        self,
        document_id: UUID,
        owner_id: Optional[str] = None,
    ) -> Optional[Document]:
        """Get document by ID."""
        statement = select(Document).where(Document.id == document_id)
        statement = self._apply_owner_scope(statement, owner_id)
        result = await self.db.execute(
            statement
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[str] = None,
    ) -> List[Document]:
        """Get all documents with pagination."""
        statement = select(Document)
        statement = self._apply_owner_scope(statement, owner_id)
        statement = statement.offset(skip).limit(limit).order_by(Document.created_at.desc())
        result = await self.db.execute(
            statement
        )
        return list(result.scalars().all())

    async def update(
        self,
        document_id: UUID,
        document_data: DocumentUpdate,
        owner_id: Optional[str] = None,
    ) -> Optional[Document]:
        """Update a document."""
        # Get existing document
        document = await self.get_by_id(document_id, owner_id=owner_id)
        if not document:
            return None

        # Update fields
        update_data = document_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)

        await self.db.flush()
        await self.db.refresh(document)

        logger.info(
            "Document updated",
            document_id=str(document_id),
            owner_id=document.owner_id,
        )
        return document

    async def delete(self, document_id: UUID, owner_id: Optional[str] = None) -> bool:
        """Delete a document."""
        statement = delete(Document).where(Document.id == document_id)
        statement = self._apply_owner_scope(statement, owner_id)
        result = await self.db.execute(
            statement
        )

        deleted = result.rowcount > 0
        if deleted:
            logger.info("Document deleted", document_id=str(document_id), owner_id=owner_id)

        return deleted

    async def update_vector_id(
        self,
        document_id: UUID,
        vector_id: str,
        owner_id: Optional[str] = None,
    ) -> Optional[Document]:
        """Update the vector ID reference for a document."""
        document = await self.get_by_id(document_id, owner_id=owner_id)
        if not document:
            return None

        document.vector_id = vector_id
        await self.db.flush()
        await self.db.refresh(document)

        logger.info(
            "Document vector ID updated",
            document_id=str(document_id),
            owner_id=document.owner_id,
            vector_id=vector_id,
        )
        return document
