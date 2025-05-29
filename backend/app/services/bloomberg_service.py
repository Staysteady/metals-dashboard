# mypy: disable-error-code=unreachable
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Bloomberg API imports
try:
    import blpapi
    BLOOMBERG_AVAILABLE = True
    logger.info("Bloomberg API package found")
except ImportError:
    BLOOMBERG_AVAILABLE = False
    logger.error("Bloomberg API package not found. Install with: pip install blpapi")


class BloombergService:
    """Service for fetching real-time and historical data from Bloomberg API"""

    def __init__(self) -> None:
        self.session: Optional[Any] = None  # blpapi.Session when available
        self.service: Optional[Any] = None  # blpapi.Service when available
        self.service_name: Optional[str] = None  # Track which service is being used
        self.is_connected = False
        self._db: Optional[Any] = None  # DatabaseConnection when loaded
        self._use_dummy_data = not BLOOMBERG_AVAILABLE  # Use dummy data if Bloomberg API not available

        # Only try to initialize Bloomberg if the package is available
        if BLOOMBERG_AVAILABLE:
            self._initialize_bloomberg()
        else:
            logger.error("Bloomberg API not available - cannot initialize connection")

    @property
    def db(self) -> Any:
        """Lazy load database connection to avoid circular imports"""
        if self._db is None:
            from ..db.connection import get_db
            self._db = get_db()
        return self._db

    def _initialize_bloomberg(self) -> None:
        """Initialize Bloomberg API connection"""
        if not BLOOMBERG_AVAILABLE:
            logger.error("Bloomberg API package not available")
            return

        try:
            # Bloomberg session options
            session_options = blpapi.SessionOptions()
            session_options.setServerHost(os.getenv("BLOOMBERG_HOST", "localhost"))
            session_options.setServerPort(int(os.getenv("BLOOMBERG_PORT", "8194")))

            # Create session
            self.session = blpapi.Session(session_options)

            # Start session
            if not self.session.start():
                logger.error("Failed to start Bloomberg session - ensure Bloomberg Terminal is running and logged in")
                return

            # Try multiple services - start with reference data service
            service_names = ["//blp/refdata", "//blp/mktdata"]
            service_opened = False
            
            for service_name in service_names:
                try:
                    if self.session.openService(service_name):
                        self.service = self.session.getService(service_name)
                        self.service_name = service_name
                        service_opened = True
                        logger.info(f"Opened Bloomberg service: {service_name}")
                        break
                except Exception as e:
                    logger.warning(f"Could not open service {service_name}: {e}")
                    continue

            if not service_opened:
                logger.error("Failed to open any Bloomberg service - check API permissions")
                return

            self.is_connected = True
            self._use_dummy_data = False  # Use real Bloomberg data when connected
            logger.info("Bloomberg API connected successfully")

        except Exception as e:
            logger.error(f"Bloomberg API initialization failed: {e}")
            self.is_connected = False

    def get_connection_status(self) -> Dict[str, Any]:
        """Get the current Bloomberg connection status"""
        return {
            "bloomberg_available": BLOOMBERG_AVAILABLE,
            "is_connected": self.is_connected,
            "status": "connected" if self.is_connected else "disconnected",
            "message": self._get_status_message()
        }

    def _get_status_message(self) -> str:
        """Get a descriptive status message"""
        if not BLOOMBERG_AVAILABLE:
            return "Bloomberg API package not installed. Install with: pip install blpapi"
        elif not self.is_connected:
            return "Bloomberg Terminal not available. Ensure Terminal is running and logged in."
        else:
            return "Connected to Bloomberg Terminal"

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

    def _cache_historical_data(self, symbol: str, data: List[Dict[str, Any]]) -> None:
        """Cache historical data in DuckDB"""
        try:
            conn = self.db.get_connection()

            # Get ticker ID
            ticker_result = conn.execute(
                "SELECT id FROM tickers WHERE symbol = ?", [symbol]
            ).fetchone()

            if not ticker_result:
                logger.warning(f"Ticker {symbol} not found for caching historical data")
                return

            ticker_id = ticker_result[0]

            # Insert historical data
            for item in data:
                date = datetime.strptime(item["date"], "%Y-%m-%d")
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
                    [max_price_id, ticker_id, symbol, date, item["price"]],
                )

            logger.info(f"Cached {len(data)} historical records for {symbol}")

        except Exception as e:
            logger.error(f"Error caching historical data: {e}")

    def _get_cached_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> Optional[List[Dict[str, Any]]]:
        """Try to get historical data from cache"""
        try:
            conn = self.db.get_connection()

            result = conn.execute(
                """
                SELECT date, px_last
                FROM price_data pd
                JOIN tickers t ON pd.ticker_id = t.id
                WHERE t.symbol = ?
                AND date >= ?
                AND date <= ?
                ORDER BY date
            """,
                [symbol, start_date, end_date],
            ).fetchall()

            if result:
                # Check if we have data for most days (at least 80% coverage)
                expected_days = (end_date - start_date).days + 1
                if len(result) >= expected_days * 0.8:
                    logger.info(
                        f"Using cached data for {symbol}: {len(result)} records"
                    )
                    return [
                        {"date": row[0].strftime("%Y-%m-%d"), "price": row[1]}
                        for row in result
                    ]

            return None

        except Exception as e:
            logger.error(f"Error reading cached data: {e}")
            return None

    def get_real_time_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get real-time price data for given symbols"""
        if not BLOOMBERG_AVAILABLE:
            logger.error("Bloomberg API package not available")
            return []

        if not self.is_connected:
            logger.warning("Bloomberg not connected, attempting to reconnect...")
            self._initialize_bloomberg()
            if not self.is_connected:
                logger.error("Failed to connect to Bloomberg Terminal")
                return []

        try:
            data = self._get_bloomberg_real_time_data(symbols)
            if data:
                self._cache_real_time_data(data)
            return data
        except Exception as e:
            logger.error(f"Error fetching real-time data from Bloomberg: {e}")
            return []

    def _get_bloomberg_real_time_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get real-time data from Bloomberg API"""
        if not self.service:
            raise RuntimeError("Bloomberg service not available")

        # Use ReferenceDataRequest which is more widely supported
        request = self.service.createRequest("ReferenceDataRequest")

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
        if not self.session:
            raise RuntimeError("Bloomberg session not available")
        
        request_id = self.session.sendRequest(request)
        logger.info(f"Sent Bloomberg request for symbols: {symbols}")

        # Process response
        results = []
        try:
            while True:
                event = self.session.nextEvent(5000)  # 5 second timeout
                
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
        # First check cache
        cached_data = self._get_cached_historical_data(symbol, start_date, end_date)
        if cached_data:
            return cached_data

        if not BLOOMBERG_AVAILABLE:
            logger.error("Bloomberg API package not available for historical data")
            return []

        if not self.is_connected:
            logger.warning("Bloomberg not connected for historical data, attempting to reconnect...")
            self._initialize_bloomberg()
            if not self.is_connected:
                logger.error("Failed to connect to Bloomberg Terminal for historical data")
                return []

        try:
            # Bloomberg API historical data request
            if not self.service:
                raise RuntimeError("Bloomberg service not available")

            # Use appropriate request type based on available service
            request_type = "HistoricalDataRequest"
            request = self.service.createRequest(request_type)

            request.getElement("securities").appendValue(symbol)
            request.getElement("fields").appendValue("PX_LAST")
            request.set("startDate", start_date.strftime("%Y%m%d"))
            request.set("endDate", end_date.strftime("%Y%m%d"))
            request.set("periodicitySelection", "DAILY")

            if not self.session:
                raise RuntimeError("Bloomberg session not available")
            
            logger.info(f"Requesting historical data for {symbol} from {start_date.date()} to {end_date.date()}")
            self.session.sendRequest(request)

            # Process response
            results = []
            while True:
                event = self.session.nextEvent(10000)  # 10 second timeout

                if event.eventType() == blpapi.Event.TIMEOUT:
                    logger.warning("Bloomberg historical data request timed out")
                    break

                elif event.eventType() == blpapi.Event.RESPONSE:
                    for msg in event:
                        if msg.hasElement("securityData"):
                            security_data = msg.getElement("securityData")
                            
                            # Check for security errors
                            if security_data.hasElement("securityError"):
                                error = security_data.getElement("securityError")
                                logger.warning(f"Security error for {symbol}: {error}")
                                break
                                
                            if security_data.hasElement("fieldData"):
                                field_data = security_data.getElement("fieldData")

                                for i in range(field_data.numValues()):
                                    data_point = field_data.getValueAsElement(i)
                                    if data_point.hasElement("date") and data_point.hasElement("PX_LAST"):
                                        date = data_point.getElementAsDatetime("date")
                                        price = data_point.getElementAsFloat("PX_LAST")

                                        results.append(
                                            {"date": date.strftime("%Y-%m-%d"), "price": price}
                                        )
                    break

            logger.info(f"Retrieved {len(results)} historical data points for {symbol}")
            
            # Cache the historical data
            if results:
                self._cache_historical_data(symbol, results)
            
            return results

        except Exception as e:
            logger.error(f"Error fetching historical data from Bloomberg: {e}")
            return []

    def close(self) -> None:
        """Close Bloomberg connection"""
        if self.session and self.is_connected:
            try:
                self.session.stop()
                logger.info("Bloomberg session closed")
            except Exception as e:
                logger.error(f"Error closing Bloomberg session: {e}")


# Global instance
bloomberg_service = BloombergService()
