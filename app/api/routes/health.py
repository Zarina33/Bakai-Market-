"""
Health check endpoints.
"""
from fastapi import APIRouter, status
from typing import Dict, Any

from app.config import settings
from app.db import postgres
from app.db.qdrant import QdrantManager

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with database connections."""
    health_status = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "components": {},
    }
    
    # Check PostgreSQL
    try:
        engine = postgres.get_engine()
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        health_status["components"]["postgres"] = "healthy"
    except Exception as e:
        health_status["components"]["postgres"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Qdrant
    try:
        qdrant_manager = QdrantManager()
        qdrant_manager.client.get_collections()
        health_status["components"]["qdrant"] = "healthy"
    except Exception as e:
        health_status["components"]["qdrant"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

