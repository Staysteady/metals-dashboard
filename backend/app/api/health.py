import logging
import os
import platform
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from app.services.bloomberg_service import bloomberg_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    
    # Get Bloomberg connection status
    bloomberg_status = bloomberg_service.get_connection_status()
    
    return {
        "status": "healthy" if bloomberg_status["is_connected"] else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.system(),
        },
        "bloomberg": bloomberg_status,
        "mode": "live_bloomberg_only",  # Only live data supported
    }


@router.get("/db")
async def database_health() -> Dict[str, Any]:
    """Database health check"""
    try:
        from ..db.connection import health_check

        return health_check()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")
