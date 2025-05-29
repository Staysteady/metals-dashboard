import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..models.ticker import (
    HistoricalData,
    HistoricalDataPoint,
    MarketStatus,
    TickerData,
)
from ..services.bloomberg_service import bloomberg_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prices", tags=["prices"])


# Default metal symbols
DEFAULT_METALS = [
    "LMCADS03",  # LME Copper 3M
    "LMAHDS03",  # LME Aluminum 3M
    "LMZSDS03",  # LME Zinc 3M
    "LMPBDS03",  # LME Lead 3M
    "LMSNDS03",  # LME Tin 3M
    "LMNIDS03",  # LME Nickel 3M
]

PRECIOUS_METALS = [
    "XAU=",  # Gold Spot
    "XAG=",  # Silver Spot
    "XPT=",  # Platinum Spot
    "XPD=",  # Palladium Spot
]


@router.get("/latest", response_model=List[TickerData])
async def get_latest_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols"),
    include_precious: bool = Query(False, description="Include precious metals"),
) -> List[TickerData]:
    """Get latest prices for metals"""
    try:
        # Parse symbols or use defaults
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]
        else:
            symbol_list = DEFAULT_METALS.copy()
            if include_precious:
                symbol_list.extend(PRECIOUS_METALS)

        # Get real-time data
        raw_data = bloomberg_service.get_real_time_data(symbol_list)

        # Convert to response model
        results = []
        for item in raw_data:
            ticker = TickerData(
                symbol=item["symbol"],
                description=item.get("description", ""),
                product_category=item.get("product_category", ""),
                px_last=item.get("px_last", 0),
                change=item.get("change"),
                change_pct=item.get("change_pct"),
                timestamp=datetime.now(timezone.utc),
            )
            results.append(ticker)

        return results

    except Exception as e:
        logger.error(f"Error fetching latest prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical/{symbol}", response_model=HistoricalData)
async def get_historical_prices(
    symbol: str,
    days: int = Query(
        30, ge=1, le=365, description="Number of days of historical data"
    ),
) -> HistoricalData:
    """Get historical prices for a specific metal"""
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # Get historical data
        raw_data = bloomberg_service.get_historical_data(symbol, start_date, end_date)

        # Convert to response model
        data_points = [
            HistoricalDataPoint(date=item["date"], price=item["price"])
            for item in raw_data
        ]

        return HistoricalData(
            symbol=symbol,
            data_points=data_points,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

    except Exception as e:
        logger.error(f"Error fetching historical prices for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-status", response_model=MarketStatus)
async def get_market_status() -> MarketStatus:
    """Get current market status"""
    now = datetime.now(timezone.utc)

    # Simple market hours check (London Metal Exchange hours)
    # LME is open Mon-Fri 01:00-19:00 UTC
    is_weekend = now.weekday() >= 5
    hour = now.hour

    if is_weekend:
        is_open = False
        message = "Market closed - Weekend"
        # Calculate next Monday 01:00 UTC
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_open = now.replace(hour=1, minute=0, second=0, microsecond=0) + timedelta(
            days=days_until_monday
        )
    elif hour < 1:
        is_open = False
        message = "Market closed - Pre-market"
        next_open = now.replace(hour=1, minute=0, second=0, microsecond=0)
    elif hour >= 19:
        is_open = False
        message = "Market closed - After hours"
        # Next day 01:00 UTC
        next_open = (now + timedelta(days=1)).replace(
            hour=1, minute=0, second=0, microsecond=0
        )
    else:
        is_open = True
        message = "Market open"
        next_close = now.replace(hour=19, minute=0, second=0, microsecond=0)

        return MarketStatus(
            is_open=is_open, message=message, next_open=None, next_close=next_close
        )

    return MarketStatus(
        is_open=is_open, message=message, next_open=next_open, next_close=None
    )


@router.get("/symbols")
async def get_available_symbols() -> Dict[str, List[Dict[str, str]]]:
    """Get list of available metal symbols"""
    return {
        "base_metals": [
            {"symbol": "LMCADS03", "description": "LME Copper 3M", "category": "CA"},
            {"symbol": "LMAHDS03", "description": "LME Aluminum 3M", "category": "AH"},
            {"symbol": "LMZSDS03", "description": "LME Zinc 3M", "category": "ZN"},
            {"symbol": "LMPBDS03", "description": "LME Lead 3M", "category": "PB"},
            {"symbol": "LMSNDS03", "description": "LME Tin 3M", "category": "SN"},
            {"symbol": "LMNIDS03", "description": "LME Nickel 3M", "category": "NI"},
        ],
        "precious_metals": [
            {"symbol": "XAU=", "description": "Gold Spot", "category": "PM"},
            {"symbol": "XAG=", "description": "Silver Spot", "category": "PM"},
            {"symbol": "XPT=", "description": "Platinum Spot", "category": "PM"},
            {"symbol": "XPD=", "description": "Palladium Spot", "category": "PM"},
        ],
    }
