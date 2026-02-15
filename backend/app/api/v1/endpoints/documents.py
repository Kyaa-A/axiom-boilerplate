"""
Document endpoints demonstrating the architecture.
Shows proper separation: API -> Repository -> Database
                        API -> AI Service -> Vector Store
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
)
from app.services.ai.chains.base_chain import embedding_chain

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a document and generate its embedding.

    Workflow:
    1. Store document in PostgreSQL (structured data)
    2. Generate embedding via Voyage AI
    3. Store embedding in Weaviate (vector data)
    4. Update document with vector reference
    """
    repo = DocumentRepository(db)

    # Create document in PostgreSQL
    document = await repo.create(document_data)

    # Generate and store embedding
    try:
        document_dict = {
            "text": document.content,
            "title": document.title,
            "source": document.source,
            "document_id": str(document.id),
        }

        vector_ids = await embedding_chain.run(
            documents=[document_dict],
            text_field="text",
        )

        # Update document with vector reference
        if vector_ids:
            await repo.update_vector_id(document.id, vector_ids[0])

    except Exception as e:
        # Document is created, but embedding failed
        # In production, this should trigger a background retry
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document created but embedding failed: {str(e)}",
        )

    return document


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a document by ID."""
    repo = DocumentRepository(db)
    document = await repo.get_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all documents with pagination."""
    repo = DocumentRepository(db)
    documents = await repo.get_all(skip=skip, limit=limit)
    return documents


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a document."""
    repo = DocumentRepository(db)
    document = await repo.update(document_id, document_data)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # TODO: Regenerate embedding if content changed
    # This should be done via a background task

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a document."""
    repo = DocumentRepository(db)
    deleted = await repo.delete(document_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # TODO: Delete vector from Weaviate
    # This should be done via a background task

    return None
