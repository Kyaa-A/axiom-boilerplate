"""
API v1 router combining all endpoints.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import documents, ai

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(documents.router)
api_router.include_router(ai.router)
