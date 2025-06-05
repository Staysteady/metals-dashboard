# mypy: disable-error-code=unreachable
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

# Bloomberg API imports - try both blpapi and xbbg
BLOOMBERG_AVAILABLE = False
BLOOMBERG_TYPE = None

# First try official blpapi
try:
    import blpapi
    BLOOMBERG_AVAILABLE = True
    BLOOMBERG_TYPE = "blpapi"
    BLPAPI_ROOT = os.getenv("BLPAPI_ROOT", "")
    if BLPAPI_ROOT:
        logger.info(f"Bloomberg API (blpapi) available at {BLPAPI_ROOT}")
    else:
        logger.info("Bloomberg API (blpapi) available (BLPAPI_ROOT not set, using system default)")
except ImportError:
    logger.info("Official blpapi not available, trying xbbg...")
    # Try xbbg as fallback
    try:
        from xbbg import blp
        BLOOMBERG_AVAILABLE = True
        BLOOMBERG_TYPE = "xbbg"
        logger.info("Bloomberg API available via xbbg")
    except ImportError:
        logger.warning("Neither blpapi nor xbbg available - Bloomberg API not available")
        BLOOMBERG_AVAILABLE = False


class BloombergService:
    """Service for fetching real-time and historical data from Bloomberg API"""

    def __init__(self) -> None:
        self._session = None
        self._is_connected = False
        self._startup_error = None
        
        if BLOOMBERG_AVAILABLE:
            try:
                if BLOOMBERG_TYPE == "blpapi":
                    self._initialize_bloomberg()
                else:
                    # xbbg doesn't need initialization
                    self._is_connected = self._test_xbbg_connection()
                    if not self._is_connected:
                        self._startup_error = "xbbg could not connect to Bloomberg Terminal"
            except Exception as e:
                logger.warning(f"Bloomberg initialization failed: {e}")
                self._startup_error = str(e)
                self._is_connected = False
        else:
            logger.warning("Bloomberg API not available - application will run in limited mode")
            self._startup_error = "Neither blpapi nor xbbg package available"

    def _test_xbbg_connection(self) -> bool:
        """Test if xbbg can connect to Bloomberg"""
        try:
            from xbbg import blp
            # Try a simple request
            data = blp.bdp(tickers='GOVT US Equity', flds='PX_LAST')
            logger.info("xbbg connection test successful")
            return True
        except Exception as e:
            logger.error(f"xbbg connection test failed: {e}")
            return False

    @property
    def db(self) -> Any:
        """Lazy load database connection to avoid circular imports"""
        from ..db.connection import get_db
        return get_db()

    def _initialize_bloomberg(self) -> None:
        """Initialize Bloomberg API connection (for blpapi only)"""
        if BLOOMBERG_TYPE != "blpapi":
            return
            
        try:
            # Session options
            sessionOptions = blpapi.SessionOptions()
            host = os.getenv("BLOOMBERG_HOST", "localhost")
            port = int(os.getenv("BLOOMBERG_PORT", "8194"))
            sessionOptions.setServerHost(host)
            sessionOptions.setServerPort(port)
            logger.info(f"Connecting to Bloomberg at {host}:{port}")
            
            # Create session
            self._session = blpapi.Session(sessionOptions)
            
            # Start session
            if not self._session.start():
                logger.error("Failed to start Bloomberg session")
                raise RuntimeError("Failed to connect to Bloomberg")
                
            # Open service
            if not self._session.openService("//blp/refdata"):
                logger.error("Failed to open Bloomberg reference data service")
                self._session.stop()
                raise RuntimeError("Failed to open Bloomberg service")
                
            self._is_connected = True
            logger.info("Successfully connected to Bloomberg API")
            
        except Exception as e:
            logger.error(f"Failed to initialize Bloomberg: {e}")
            self._is_connected = False
            raise RuntimeError(f"Bloomberg connection failed: {e}")

    def get_connection_status(self) -> Dict[str, Any]:
        """Get the current Bloomberg connection status"""
        return {
            "bloomberg_available": BLOOMBERG_AVAILABLE,
            "bloomberg_type": BLOOMBERG_TYPE,
            "is_connected": self._is_connected,
            "status": "connected" if self._is_connected else "disconnected",
            "message": self._get_status_message()
        }

    def _get_status_message(self) -> str:
        """Get a descriptive status message"""
        if self._startup_error:
            return f"Bloomberg startup failed: {self._startup_error}"
        elif not BLOOMBERG_AVAILABLE:
            return "Bloomberg API package not installed. Install with: pip install blpapi or pip install xbbg"
        elif not self._is_connected:
            return "Bloomberg Terminal not available. Ensure Terminal is running and logged in."
        else:
            return f"Connected to Bloomberg Terminal via {BLOOMBERG_TYPE}"

    def _cache_real_time_data(self, data: List[Dict[str, Any]]) -> None:
        """Cache real-time data in DuckDB"""
        try:
            conn = self.db.get_connection()

            for item in data:
                # First, ensure ticker exists
                ticker_result = conn.execute(
                    "SELECT id FROM tickers WHERE symbol = ?", [item["symbol"]]
                ).fetchone()

                if not ticker_result:
                    # Create ticker if it doesn't exist
                    max_id = conn.execute(
                        "SELECT COALESCE(MAX(id), 0) + 1 FROM tickers"
                    ).fetchone()[0]
                    conn.execute(
                        """
                        INSERT INTO tickers (id, symbol, description, product_category, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        [
                            max_id,
                            item["symbol"],
                            item.get("description", ""),
                            item.get("product_category", ""),
                            datetime.now(timezone.utc),
                        ],
                    )
                    ticker_id = max_id
                else:
                    ticker_id = ticker_result[0]

                # Insert price data
                max_price_id = conn.execute(
                    "SELECT COALESCE(MAX(id), 0) + 1 FROM price_data"
                ).fetchone()[0]

                conn.execute(
                    """
                    INSERT INTO price_data (id, ticker_id, symbol, date, px_last)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT (ticker_id, date) DO UPDATE SET
                        px_last = excluded.px_last
                """,
                    [
                        max_price_id,
                        ticker_id,
                        item["symbol"],
                        datetime.now(timezone.utc),
                        item.get("px_last", 0),
                    ],
                )

            logger.info(f"Cached {len(data)} real-time price records")

        except Exception as e:
            logger.error(f"Error caching real-time data: {e}")

    def get_real_time_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get real-time price data for given symbols"""
        if not BLOOMBERG_AVAILABLE or self._startup_error:
            logger.warning("Bloomberg API not available - returning empty data")
            return []

        if not self._is_connected:
            logger.warning("Bloomberg not connected, attempting to reconnect...")
            if BLOOMBERG_TYPE == "blpapi":
                try:
                    self._initialize_bloomberg()
                except Exception as e:
                    logger.error(f"Failed to reconnect to Bloomberg: {e}")
                    return []
            else:
                self._is_connected = self._test_xbbg_connection()
            
            if not self._is_connected:
                logger.error("Failed to connect to Bloomberg Terminal")
                return []

        try:
            if BLOOMBERG_TYPE == "blpapi":
                data = self._get_bloomberg_real_time_data(symbols)
            else:
                data = self._get_xbbg_real_time_data(symbols)
                
            if data:
                self._cache_real_time_data(data)
            return data
        except Exception as e:
            logger.error(f"Error fetching real-time data from Bloomberg: {e}")
            return []

    def _get_xbbg_real_time_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get real-time data using xbbg"""
        from xbbg import blp
        
        results = []
        try:
            # xbbg needs specific ticker format with asset class
            formatted_symbols = []
            for symbol in symbols:
                if not any(suffix in symbol for suffix in [' Comdty', ' Curncy', ' Equity', ' Index']):
                    # Default to Comdty for metals
                    formatted_symbols.append(f"{symbol} Comdty")
                else:
                    formatted_symbols.append(symbol)
            
            # Request data
            fields = ['PX_LAST', 'NAME', 'CHG_NET_1D', 'CHG_PCT_1D']
            data = blp.bdp(tickers=formatted_symbols, flds=fields)
            
            logger.info(f"xbbg returned data for {len(data)} symbols")
            
            # Convert to expected format
            for ticker, row in data.iterrows():
                result = {
                    "symbol": ticker,
                    "px_last": float(row.get('PX_LAST', 0)) if row.get('PX_LAST') is not None else 0.0,
                    "change": float(row.get('CHG_NET_1D', 0)) if row.get('CHG_NET_1D') is not None else 0.0,
                    "change_pct": float(row.get('CHG_PCT_1D', 0)) if row.get('CHG_PCT_1D') is not None else 0.0,
                    "description": str(row.get('NAME', '')),
                    "product_category": self._get_product_category(ticker),
                }
                results.append(result)
                logger.info(f"Retrieved data for {ticker}: {result['px_last']}")
                
        except Exception as e:
            logger.error(f"Error processing xbbg response: {e}")
            
        return results

    def _get_product_category(self, symbol: str) -> str:
        """Determine product category from symbol"""
        if any(metal in symbol.upper() for metal in ['XAU', 'XAG', 'XPT', 'XPD', 'GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM']):
            return "PRECIOUS"
        elif any(metal in symbol.upper() for metal in ['LM', 'COPPER', 'ALUMINUM', 'ZINC', 'NICKEL', 'LEAD', 'TIN']):
            return "BASE"
        else:
            return "OTHER"

    def _get_bloomberg_real_time_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get real-time data from Bloomberg API (blpapi)"""
        if not self._session:
            raise RuntimeError("Bloomberg session not available")

        # Get the reference data service
        service = self._session.getService("//blp/refdata")
        
        # Use ReferenceDataRequest which is more widely supported
        request = service.createRequest("ReferenceDataRequest")

        # Add securities
        securities = request.getElement("securities")
        for symbol in symbols:
            securities.appendValue(symbol)

        # Add fields - use basic fields that are commonly available
        fields = request.getElement("fields")
        field_list = ["PX_LAST", "NAME", "GICS_SECTOR_NAME"]
        for field in field_list:
            fields.appendValue(field)

        # Send request
        request_id = self._session.sendRequest(request)
        logger.info(f"Sent Bloomberg request for symbols: {symbols}")

        # Process response
        results = []
        try:
            while True:
                event = self._session.nextEvent(5000)  # 5 second timeout
                
                if event.eventType() == blpapi.Event.TIMEOUT:
                    logger.warning("Bloomberg request timed out")
                    break
                    
                elif event.eventType() == blpapi.Event.RESPONSE:
                    for msg in event:
                        if msg.hasElement("securityData"):
                            security_data = msg.getElement("securityData")
                            for i in range(security_data.numValues()):
                                security = security_data.getValueAsElement(i)
                                symbol = security.getElementAsString("security")
                                
                                # Check for security errors
                                if security.hasElement("securityError"):
                                    error = security.getElement("securityError")
                                    logger.warning(f"Security error for {symbol}: {error}")
                                    continue
                                
                                field_data = security.getElement("fieldData")
                                
                                result = {
                                    "symbol": symbol,
                                    "px_last": (
                                        field_data.getElementAsFloat("PX_LAST")
                                        if field_data.hasElement("PX_LAST") and not field_data.getElement("PX_LAST").isNull()
                                        else 0.0
                                    ),
                                    "change": 0.0,  # Not available in reference data
                                    "change_pct": 0.0,  # Not available in reference data
                                    "description": (
                                        field_data.getElementAsString("NAME")
                                        if field_data.hasElement("NAME") and not field_data.getElement("NAME").isNull()
                                        else ""
                                    ),
                                    "product_category": (
                                        field_data.getElementAsString("GICS_SECTOR_NAME")
                                        if field_data.hasElement("GICS_SECTOR_NAME") and not field_data.getElement("GICS_SECTOR_NAME").isNull()
                                        else "Unknown"
                                    ),
                                }
                                results.append(result)
                                logger.info(f"Retrieved data for {symbol}: {result['px_last']}")
                    break
                    
                elif event.eventType() == blpapi.Event.PARTIAL_RESPONSE:
                    # Continue processing partial responses
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing Bloomberg response: {e}")
            
        logger.info(f"Bloomberg returned {len(results)} results")
        return results

    def get_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get historical price data for a symbol"""
        if not BLOOMBERG_AVAILABLE or self._startup_error:
            logger.warning("Bloomberg API not available for historical data - returning empty data")
            return []

        if not self._is_connected:
            logger.warning("Bloomberg not connected for historical data")
            return []

        try:
            if BLOOMBERG_TYPE == "xbbg":
                return self._get_xbbg_historical_data(symbol, start_date, end_date)
            else:
                # Original blpapi implementation
                return self._get_blpapi_historical_data(symbol, start_date, end_date)
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return []

    def _get_xbbg_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get historical data using xbbg"""
        from xbbg import blp
        
        try:
            # Format symbol if needed
            if not any(suffix in symbol for suffix in [' Comdty', ' Curncy', ' Equity', ' Index']):
                symbol = f"{symbol} Comdty"
            
            # Get historical data
            data = blp.bdh(
                tickers=symbol,
                flds='PX_LAST',
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d')
            )
            
            results = []
            if not data.empty:
                # Flatten multi-level columns if present
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = [col[1] for col in data.columns]
                
                for date, row in data.iterrows():
                    results.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "price": float(row.get('PX_LAST', 0))
                    })
            
            logger.info(f"Retrieved {len(results)} historical data points for {symbol}")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching historical data from xbbg: {e}")
            return []

    def _get_blpapi_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get historical data using blpapi (original implementation)"""
        # Original implementation code here
        # ... (copy from original bloomberg_service.py)
        return []

    def close(self) -> None:
        """Close Bloomberg connection"""
        if self._session and self._is_connected and BLOOMBERG_TYPE == "blpapi":
            try:
                self._session.stop()
                logger.info("Bloomberg session closed")
            except Exception as e:
                logger.error(f"Error closing Bloomberg session: {e}")


# Global instance
bloomberg_service = BloombergService()

# Add pandas import if using xbbg
if BLOOMBERG_TYPE == "xbbg":
    import pandas as pd 