import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from .api.health import router as health_router
from .api.prices import router as prices_router
from .api.settings import router as settings_router
from .api.lme import router as lme_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan"""
    # Startup
    try:
        # Initialize database
        from .db.connection import init_database

        init_database()

        # Initialize Bloomberg service
        from .services.bloomberg_service import bloomberg_service
        status = bloomberg_service.get_connection_status()
        logger.info(f"Application starting - Bloomberg Status: {status['status']}")
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Shutdown
    try:
        from .services.bloomberg_service import bloomberg_service

        bloomberg_service.close()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


app = FastAPI(
    title="Metals Dashboard API",
    description="API for metals trading dashboard with Bloomberg integration",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(prices_router)
app.include_router(settings_router)
app.include_router(lme_router)


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "Metals Dashboard API",
        "version": "1.0.0",
        "phase": "3",
        "endpoints": {
            "health": "/health/",
            "prices": {
                "latest": "/prices/latest",
                "historical": "/prices/historical/{symbol}?days=30",
                "symbols": "/prices/symbols",
                "market_status": "/prices/market-status",
            },
            "lme": {
                "tickers": "/lme/tickers",
                "add_ticker": "/lme/tickers/add",
                "market_status": "/lme/market-status"
            },
            "settings": {
                "bloomberg_status": "/settings/bloomberg-status",
                "data_source_status": "/settings/data-source-status",
                "reconnect": "/settings/reconnect-bloomberg"
            }
        },
    }


@app.get("/ping")
async def ping() -> Dict[str, str]:
    """Simple ping endpoint"""
    return {"status": "ok"}
