import logging
import os
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check_endpoint() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        from ..db.connection import health_check

        # Get database health
        db_health = health_check()

        # Determine if using dummy data
        use_dummy_data = os.getenv("USE_DUMMY_DATA", "true").lower() == "true"

        return {
            "status": "healthy",
            "service": "Metals Dashboard API",
            "phase": "3",
            "mode": "dummy_data" if use_dummy_data else "bloomberg",
            "database": db_health,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.get("/db")
async def database_health() -> Dict[str, Any]:
    """Database health check"""
    try:
        from ..db.connection import health_check

        return health_check()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")
