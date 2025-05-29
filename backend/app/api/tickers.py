import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..models.ticker import (
    PriceDataResponse,
    ProductCategory,
    Ticker,
    TickerCreate,
    TickerUpdate,
)
from ..services.ticker_service import TickerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickers", tags=["tickers"])


def get_ticker_service() -> TickerService:
    """Dependency to get ticker service"""
    return TickerService()


@router.get("/", response_model=List[Ticker])
async def get_tickers(
    product_category: Optional[str] = Query(
        None, description="Filter by product category"
    ),
    ticker_service: TickerService = Depends(get_ticker_service),
) -> List[Ticker]:
    """Get all tickers, optionally filtered by product category"""
    try:
        return ticker_service.get_all_tickers(product_category)
    except Exception as e:
        logger.error(f"Error getting tickers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search", response_model=List[Ticker])
async def search_tickers(
    q: str = Query(..., description="Search query"),
    ticker_service: TickerService = Depends(get_ticker_service),
) -> List[Ticker]:
    """Search tickers by symbol or description"""
    try:
        return ticker_service.search_tickers(q)
    except Exception as e:
        logger.error(f"Error searching tickers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/latest-prices")
async def get_latest_prices(
    product_category: Optional[str] = Query(
        None, description="Filter by product category"
    ),
    ticker_service: TickerService = Depends(get_ticker_service),
) -> List[Dict[str, Any]]:
    """Get latest prices for all tickers"""
    try:
        return ticker_service.get_latest_prices(product_category)
    except Exception as e:
        logger.error(f"Error getting latest prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{ticker_id}", response_model=Ticker)
async def get_ticker(
    ticker_id: int, ticker_service: TickerService = Depends(get_ticker_service)
) -> Ticker:
    """Get ticker by ID"""
    try:
        ticker = ticker_service.get_ticker_by_id(ticker_id)
        if not ticker:
            raise HTTPException(status_code=404, detail="Ticker not found")
        return ticker
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticker {ticker_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Ticker, status_code=201)
async def create_ticker(
    ticker_data: TickerCreate,
    ticker_service: TickerService = Depends(get_ticker_service),
) -> Ticker:
    """Create a new ticker"""
    try:
        return ticker_service.create_ticker(ticker_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating ticker: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{ticker_id}", response_model=Ticker)
async def update_ticker(
    ticker_id: int,
    ticker_data: TickerUpdate,
    ticker_service: TickerService = Depends(get_ticker_service),
) -> Ticker:
    """Update an existing ticker"""
    try:
        ticker = ticker_service.update_ticker(ticker_id, ticker_data)
        if not ticker:
            raise HTTPException(status_code=404, detail="Ticker not found")
        return ticker
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticker {ticker_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{ticker_id}", status_code=204)
async def delete_ticker(
    ticker_id: int, ticker_service: TickerService = Depends(get_ticker_service)
) -> None:
    """Delete a ticker"""
    try:
        success = ticker_service.delete_ticker(ticker_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ticker not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting ticker {ticker_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{ticker_id}/prices", response_model=PriceDataResponse)
async def get_ticker_prices(
    ticker_id: int,
    start_date: Optional[datetime] = Query(
        None, description="Start date for price data"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for price data"),
    limit: Optional[int] = Query(
        None, description="Maximum number of records to return"
    ),
    ticker_service: TickerService = Depends(get_ticker_service),
) -> PriceDataResponse:
    """Get price data for a ticker"""
    try:
        price_data = ticker_service.get_price_data(
            ticker_id, start_date, end_date, limit
        )
        if not price_data:
            raise HTTPException(status_code=404, detail="Ticker not found")
        return price_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prices for ticker {ticker_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/categories/", response_model=List[str])
async def get_product_categories() -> List[str]:
    """Get all available product categories"""
    return [category.value for category in ProductCategory]
