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
        self.is_connected = False
        self._db: Optional[Any] = None  # DatabaseConnection when loaded

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

            if not self.session.openService("//blp/mktdata"):
                logger.error("Failed to open Bloomberg market data service - check API permissions")
                return

            self.service = self.session.getService("//blp/mktdata")
            self.is_connected = True
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

        request = self.service.createRequest("SnapshotDataRequest")

        # Add securities
        for symbol in symbols:
            request.getElement("securities").appendValue(symbol)

        # Add fields
        fields = ["PX_LAST", "CHANGE", "CHANGE_PCT", "DESCRIPTION", "PRODUCT_CATEGORY"]
        for field in fields:
            request.getElement("fields").appendValue(field)

        # Send request
        if not self.session:
            raise RuntimeError("Bloomberg session not available")
        self.session.sendRequest(request)

        # Process response
        results = []
        while True:
            event = self.session.nextEvent(500)

            if event.eventType() == blpapi.Event.RESPONSE:
                for msg in event:
                    security_data = msg.getElement("securityData")
                    for i in range(security_data.numValues()):
                        security = security_data.getValueAsElement(i)
                        symbol = security.getElementAsString("security")
                        field_data = security.getElement("fieldData")

                        result = {
                            "symbol": symbol,
                            "px_last": (
                                field_data.getElementAsFloat("PX_LAST")
                                if field_data.hasElement("PX_LAST")
                                else None
                            ),
                            "change": (
                                field_data.getElementAsFloat("CHANGE")
                                if field_data.hasElement("CHANGE")
                                else None
                            ),
                            "change_pct": (
                                field_data.getElementAsFloat("CHANGE_PCT")
                                if field_data.hasElement("CHANGE_PCT")
                                else None
                            ),
                            "description": (
                                field_data.getElementAsString("DESCRIPTION")
                                if field_data.hasElement("DESCRIPTION")
                                else ""
                            ),
                            "product_category": (
                                field_data.getElementAsString("PRODUCT_CATEGORY")
                                if field_data.hasElement("PRODUCT_CATEGORY")
                                else ""
                            ),
                        }
                        results.append(result)
                break

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

            request = self.service.createRequest("HistoricalDataRequest")

            request.getElement("securities").appendValue(symbol)
            request.getElement("fields").appendValue("PX_LAST")
            request.set("startDate", start_date.strftime("%Y%m%d"))
            request.set("endDate", end_date.strftime("%Y%m%d"))
            request.set("periodicitySelection", "DAILY")

            if not self.session:
                raise RuntimeError("Bloomberg session not available")
            self.session.sendRequest(request)

            # Process response
            results = []
            while True:
                event = self.session.nextEvent(500)

                if event.eventType() == blpapi.Event.RESPONSE:
                    for msg in event:
                        security_data = msg.getElement("securityData")
                        field_data = security_data.getElement("fieldData")

                        for i in range(field_data.numValues()):
                            data_point = field_data.getValueAsElement(i)
                            date = data_point.getElementAsDatetime("date")
                            price = data_point.getElementAsFloat("PX_LAST")

                            results.append(
                                {"date": date.strftime("%Y-%m-%d"), "price": price}
                            )
                    break

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
