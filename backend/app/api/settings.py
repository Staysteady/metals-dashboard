import logging

from fastapi import APIRouter, HTTPException

from ..services.bloomberg_service import bloomberg_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/bloomberg-status")
async def get_bloomberg_status() -> dict:
    """Get current Bloomberg connection status"""
    try:
        status = bloomberg_service.get_connection_status()
        return {
            "bloomberg_available": status["bloomberg_available"],
            "is_connected": status["is_connected"],
            "status": status["status"],
            "message": status["message"]
        }

    except Exception as e:
        logger.error(f"Error getting Bloomberg status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-source-status")
async def get_data_source_status() -> dict:
    """Get current data source status and information"""
    try:
        status = bloomberg_service.get_connection_status()
        
        if status["is_connected"]:
            data_status = "connected"
            message = "Connected to Bloomberg Terminal - Live data available"
        elif status["bloomberg_available"]:
            data_status = "disconnected"
            message = "Bloomberg API available but not connected to Terminal"
        else:
            data_status = "unavailable"
            message = "Bloomberg API not installed. Install with: pip install blpapi"

        return {
            "status": data_status,
            "message": message,
            "bloomberg_available": status["bloomberg_available"],
            "is_connected": status["is_connected"]
        }

    except Exception as e:
        logger.error(f"Error getting data source status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reconnect-bloomberg")
async def reconnect_bloomberg() -> dict:
    """Attempt to reconnect to Bloomberg Terminal"""
    try:
        # Reinitialize Bloomberg connection
        bloomberg_service._initialize_bloomberg()
        status = bloomberg_service.get_connection_status()
        
        return {
            "success": status["is_connected"],
            "message": status["message"],
            "status": status["status"]
        }

    except Exception as e:
        logger.error(f"Error reconnecting to Bloomberg: {e}")
        raise HTTPException(status_code=500, detail=str(e))
