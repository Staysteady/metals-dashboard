import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..models.ticker import Ticker, TickerCreate
from ..services.bloomberg_service import bloomberg_service
from ..services.ticker_service import TickerService
from ..db.lme_tickers import get_lme_tickers, get_bloomberg_symbols

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lme", tags=["lme"])

# Initialize services
ticker_service = TickerService()

class LMETickerData(BaseModel):
    """LME ticker data with live Bloomberg prices"""
    id: int  # Add database ID for deletion
    ticker: str
    description: str  
    metal: str
    symbol: str
    bloomberg_symbol: str
    px_last: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    timestamp: Optional[datetime] = None
    is_live: bool = False

class AddTickerRequest(BaseModel):
    """Request to add a new Bloomberg ticker"""
    bloomberg_symbol: str
    description: Optional[str] = None
    metal: Optional[str] = None
    symbol: Optional[str] = None

class TickerSearchResult(BaseModel):
    """Simplified ticker data for search/dropdown results"""
    id: int
    symbol: str
    description: str
    product_category: str
    is_custom: bool

@router.get("/tickers", response_model=List[LMETickerData])
async def get_lme_tickers_with_prices(
    include_live_prices: bool = Query(default=True, description="Include live Bloomberg prices")
) -> List[LMETickerData]:
    """
    Get all tickers with optional live Bloomberg prices
    """
    try:
        # Get all tickers from database (not just LME/metals)
        db_tickers = ticker_service.get_all_tickers()
        
        # If no tickers in DB, initialize with default LME tickers for demo purposes
        if not db_tickers:
            logger.info("No tickers found in database, initializing defaults...")
            await initialize_default_lme_tickers()
            db_tickers = ticker_service.get_all_tickers()

        # Get live prices if requested
        live_prices = {}
        if include_live_prices and db_tickers:
            bloomberg_symbols = [ticker.symbol for ticker in db_tickers]
            try:
                price_data = bloomberg_service.get_real_time_data(bloomberg_symbols)
                live_prices = {item["symbol"]: item for item in price_data}
                logger.info(f"Retrieved live prices for {len(live_prices)} tickers")
            except Exception as e:
                logger.error(f"Error fetching live prices: {e}")
        
        # Build response
        result = []
        for ticker in db_tickers:
            price_info = live_prices.get(ticker.symbol, {})
            
            result.append(LMETickerData(
                id=ticker.id,
                ticker=ticker.symbol,
                description=ticker.description,
                metal=extract_metal_from_symbol(ticker.symbol),
                symbol=ticker.product_category or "OTHER",
                bloomberg_symbol=ticker.symbol,
                px_last=price_info.get("px_last"),
                change=price_info.get("change"),
                change_pct=price_info.get("change_pct"),
                timestamp=datetime.now(timezone.utc) if price_info else None,
                is_live=bool(price_info)  # All data is live since dummy data is removed
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching tickers: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching ticker data: {str(e)}")

@router.post("/tickers/add", response_model=Dict[str, str])
async def add_bloomberg_ticker(request: AddTickerRequest) -> Dict[str, str]:
    """
    Add a new Bloomberg ticker to the tracking list
    This will validate the ticker against Bloomberg API and store it in database
    Only symbol is required - all other fields are optional
    """
    try:
        # Validate ticker exists in Bloomberg
        logger.info(f"Validating Bloomberg ticker: {request.bloomberg_symbol}")
        
        # Try to get data from Bloomberg to validate ticker
        price_data = bloomberg_service.get_real_time_data([request.bloomberg_symbol])
        
        # Require valid price data from Bloomberg to consider ticker valid
        if not price_data or not price_data[0] or price_data[0].get("px_last") is None:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid Bloomberg ticker: {request.bloomberg_symbol}. Ticker not found or no price data available from Bloomberg API."
            )
        
        # Extract metadata from Bloomberg response or use provided values
        description = request.description or price_data[0].get("description", f"{request.bloomberg_symbol} Price")
        
        # Use Bloomberg category if available, otherwise use provided or default to "OTHER"
        product_category = price_data[0].get("product_category") or request.symbol or "OTHER"
        
        # Check if ticker already exists
        existing_ticker = ticker_service.get_ticker_by_symbol(request.bloomberg_symbol)
        if existing_ticker:
            return {
                "status": "already_exists",
                "message": f"Ticker {request.bloomberg_symbol} already exists in database",
                "ticker_id": str(existing_ticker.id)
            }
        
        # Create new ticker with minimal required data
        new_ticker = ticker_service.create_ticker(TickerCreate(
            symbol=request.bloomberg_symbol,
            description=description,
            product_category=product_category,
            is_custom=True
        ))
        
        logger.info(f"Successfully added Bloomberg ticker: {request.bloomberg_symbol}")
        
        return {
            "status": "success",
            "message": f"Successfully added ticker {request.bloomberg_symbol}",
            "ticker_id": str(new_ticker.id),
            "description": description,
            "current_price": str(price_data[0].get("px_last", "N/A"))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding Bloomberg ticker {request.bloomberg_symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding ticker: {str(e)}")

@router.delete("/tickers/{ticker_id}")
async def delete_lme_ticker(ticker_id: int) -> Dict[str, str]:
    """Delete an LME ticker from tracking"""
    try:
        success = ticker_service.delete_ticker(ticker_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ticker not found")
        
        return {"status": "success", "message": f"Ticker {ticker_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting ticker {ticker_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting ticker: {str(e)}")

@router.get("/market-status")
async def get_lme_market_status() -> Dict[str, Any]:
    """Get LME market status and trading hours"""
    try:
        # This would typically check LME trading hours
        # For now, return a basic status
        current_time = datetime.now(timezone.utc)
        
        # LME trades Monday-Friday, roughly 01:00-19:00 GMT
        is_weekend = current_time.weekday() >= 5
        hour = current_time.hour
        
        is_open = not is_weekend and 1 <= hour <= 19
        
        return {
            "is_open": is_open,
            "exchange": "LME",
            "current_time": current_time.isoformat(),
            "message": "LME Market Open" if is_open else "LME Market Closed",
            "trading_hours": "01:00-19:00 GMT (Mon-Fri)"
        }
        
    except Exception as e:
        logger.error(f"Error getting LME market status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting market status: {str(e)}")

async def initialize_default_lme_tickers():
    """Initialize database with default LME tickers"""
    try:
        default_tickers = get_lme_tickers()
        
        for ticker_data in default_tickers:
            try:
                # Check if ticker already exists
                existing = ticker_service.get_ticker_by_symbol(ticker_data["bloomberg_symbol"])
                if not existing:
                    ticker_service.create_ticker(TickerCreate(
                        symbol=ticker_data["bloomberg_symbol"],
                        description=ticker_data["description"],
                        product_category="LME_BASE_METALS",
                        is_custom=False
                    ))
                    logger.info(f"Added default LME ticker: {ticker_data['bloomberg_symbol']}")
            except Exception as e:
                logger.error(f"Error adding default ticker {ticker_data['bloomberg_symbol']}: {e}")
                
        logger.info("Default LME tickers initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing default LME tickers: {e}")

def extract_metal_from_symbol(bloomberg_symbol: str) -> str:
    """Extract metal name from Bloomberg symbol"""
    metal_map = {
        "LMAH": "Aluminium",
        "LMCA": "Copper", 
        "LMNI": "Nickel",
        "LMPB": "Lead",
        "LMSN": "Tin",
        "LMZN": "Zinc",
        "LMZS": "Zinc"  # Alternative zinc code
    }
    
    for code, metal in metal_map.items():
        if bloomberg_symbol.startswith(code):
            return metal
    
    return "Unknown"

def extract_symbol_from_bloomberg(bloomberg_symbol: str) -> str:
    """Extract short symbol from Bloomberg symbol"""
    symbol_map = {
        "LMAH": "AH",
        "LMCA": "CA",
        "LMNI": "NI", 
        "LMPB": "PB",
        "LMSN": "SN",
        "LMZN": "ZN",
        "LMZS": "ZN"
    }
    
    for code, symbol in symbol_map.items():
        if bloomberg_symbol.startswith(code):
            return symbol
            
    return bloomberg_symbol[:2].upper()

@router.get("/search", response_model=List[TickerSearchResult])
async def search_tickers(
    q: str = Query(..., description="Search query - searches symbol, description, and category"),
    limit: int = Query(default=20, description="Maximum number of results")
) -> List[TickerSearchResult]:
    """
    Search tickers by symbol, description, or category
    Returns simplified results suitable for dropdowns/autocomplete
    """
    try:
        db_tickers = ticker_service.get_all_tickers()
        
        # Filter tickers based on search query
        search_query = q.lower()
        filtered_tickers = []
        
        for ticker in db_tickers:
            # Search in symbol, description, and product_category
            if (search_query in ticker.symbol.lower() or 
                search_query in ticker.description.lower() or 
                search_query in (ticker.product_category or "").lower()):
                filtered_tickers.append(ticker)
        
        # Sort by relevance (exact symbol match first, then starts with, then contains)
        def sort_key(ticker):
            symbol_lower = ticker.symbol.lower()
            desc_lower = ticker.description.lower()
            
            if symbol_lower == search_query:
                return (0, ticker.symbol)  # Exact match
            elif symbol_lower.startswith(search_query):
                return (1, ticker.symbol)  # Starts with
            elif desc_lower.startswith(search_query):
                return (2, ticker.symbol)  # Description starts with
            else:
                return (3, ticker.symbol)  # Contains
        
        filtered_tickers.sort(key=sort_key)
        
        # Convert to search results and limit
        results = []
        for ticker in filtered_tickers[:limit]:
            results.append(TickerSearchResult(
                id=ticker.id,
                symbol=ticker.symbol,
                description=ticker.description,
                product_category=ticker.product_category or "OTHER",
                is_custom=ticker.is_custom
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching tickers: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching tickers: {str(e)}") 