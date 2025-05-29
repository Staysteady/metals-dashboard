import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..db.connection import get_db
from ..models.ticker import (
    PriceData,
    PriceDataResponse,
    Ticker,
    TickerCreate,
    TickerUpdate,
)

logger = logging.getLogger(__name__)


class TickerService:
    """Service for managing tickers and price data"""

    def __init__(self) -> None:
        self.db = get_db()

    def get_all_tickers(self, product_category: Optional[str] = None) -> List[Ticker]:
        """Get all tickers, optionally filtered by product category"""
        query = "SELECT * FROM tickers"
        params = []

        if product_category:
            query += " WHERE product_category = ?"
            params.append(product_category)

        query += " ORDER BY product_category, symbol"

        rows = self.db.fetchall(query, params if params else None)

        return [
            Ticker(
                id=row[0],
                symbol=row[1],
                description=row[2],
                product_category=row[3],
                is_custom=bool(row[4]),
                created_at=row[5],
                updated_at=row[6],
            )
            for row in rows
        ]

    def get_ticker_by_id(self, ticker_id: int) -> Optional[Ticker]:
        """Get ticker by ID"""
        row = self.db.fetchone("SELECT * FROM tickers WHERE id = ?", [ticker_id])

        if not row:
            return None

        return Ticker(
            id=row[0],
            symbol=row[1],
            description=row[2],
            product_category=row[3],
            is_custom=bool(row[4]),
            created_at=row[5],
            updated_at=row[6],
        )

    def get_ticker_by_symbol(self, symbol: str) -> Optional[Ticker]:
        """Get ticker by symbol"""
        row = self.db.fetchone("SELECT * FROM tickers WHERE symbol = ?", [symbol])

        if not row:
            return None

        return Ticker(
            id=row[0],
            symbol=row[1],
            description=row[2],
            product_category=row[3],
            is_custom=bool(row[4]),
            created_at=row[5],
            updated_at=row[6],
        )

    def create_ticker(self, ticker_data: TickerCreate) -> Ticker:
        """Create a new ticker"""
        conn = self.db.get_connection()

        # Check if symbol already exists
        existing = self.get_ticker_by_symbol(ticker_data.symbol)
        if existing:
            raise ValueError(f"Ticker with symbol {ticker_data.symbol} already exists")

        # Get next available ID
        max_id_result = conn.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM tickers"
        ).fetchone()

        if max_id_result is None:
            raise RuntimeError("Failed to get next ID")

        next_id = max_id_result[0]

        # Prepare values with sensible defaults
        description = ticker_data.description or f"{ticker_data.symbol} Price"
        product_category = ticker_data.product_category or "OTHER"

        # Insert new ticker
        conn.execute(
            """
            INSERT INTO tickers (id, symbol, description, product_category, is_custom, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            [
                next_id,
                ticker_data.symbol,
                description,
                product_category,
                ticker_data.is_custom,
                datetime.now(),
            ],
        )

        # Return the created ticker
        result = self.get_ticker_by_id(next_id)
        if result is None:
            raise RuntimeError("Failed to create ticker")
        return result

    def update_ticker(
        self, ticker_id: int, ticker_data: TickerUpdate
    ) -> Optional[Ticker]:
        """Update an existing ticker"""
        ticker = self.get_ticker_by_id(ticker_id)
        if not ticker:
            return None

        # Build update query dynamically
        updates = []
        params: List[Any] = []

        if ticker_data.description is not None:
            updates.append("description = ?")
            params.append(ticker_data.description)

        if ticker_data.product_category is not None:
            updates.append("product_category = ?")
            params.append(ticker_data.product_category.value)

        if not updates:
            return ticker

        updates.append("updated_at = ?")
        params.append(datetime.now())
        params.append(ticker_id)

        query = f"UPDATE tickers SET {', '.join(updates)} WHERE id = ?"
        self.db.execute(query, params)

        return self.get_ticker_by_id(ticker_id)

    def delete_ticker(self, ticker_id: int) -> bool:
        """Delete a ticker and its price data"""
        ticker = self.get_ticker_by_id(ticker_id)
        if not ticker:
            return False

        conn = self.db.get_connection()

        # Delete price data first (foreign key constraint)
        conn.execute("DELETE FROM price_data WHERE ticker_id = ?", (ticker_id,))

        # Delete ticker
        conn.execute("DELETE FROM tickers WHERE id = ?", (ticker_id,))

        logger.info(f"Deleted ticker {ticker.symbol} (ID: {ticker_id})")
        return True

    def get_price_data(
        self,
        ticker_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Optional[PriceDataResponse]:
        """Get price data for a ticker"""
        ticker = self.get_ticker_by_id(ticker_id)
        if not ticker:
            return None

        # Build query
        query = "SELECT * FROM price_data WHERE ticker_id = ?"
        params: List[Any] = [ticker_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        rows = self.db.fetchall(query, params)

        prices = [
            PriceData(
                ticker_id=row[1],
                symbol=row[2],
                date=row[3],
                px_last=row[4],
                px_open=row[5],
                px_high=row[6],
                px_low=row[7],
                px_volume=row[8],
            )
            for row in rows
        ]

        return PriceDataResponse(
            ticker=ticker, prices=prices, total_records=len(prices)
        )

    def get_latest_prices(
        self, product_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get latest prices for all tickers"""
        query = """
            SELECT t.id, t.symbol, t.description, t.product_category,
                   p.px_last, p.date, p.px_open, p.px_high, p.px_low
            FROM tickers t
            LEFT JOIN (
                SELECT ticker_id, px_last, date, px_open, px_high, px_low,
                       ROW_NUMBER() OVER (PARTITION BY ticker_id ORDER BY date DESC) as rn
                FROM price_data
            ) p ON t.id = p.ticker_id AND p.rn = 1
        """

        params = []
        if product_category:
            query += " WHERE t.product_category = ?"
            params.append(product_category)

        query += " ORDER BY t.product_category, t.symbol"

        rows = self.db.fetchall(query, params if params else None)

        return [
            {
                "ticker_id": row[0],
                "symbol": row[1],
                "description": row[2],
                "product_category": row[3],
                "px_last": row[4],
                "date": row[5],
                "px_open": row[6],
                "px_high": row[7],
                "px_low": row[8],
                "change": round((row[4] - row[6]) if row[4] and row[6] else 0, 2),
                "change_pct": round(
                    (
                        ((row[4] - row[6]) / row[6] * 100)
                        if row[4] and row[6] and row[6] != 0
                        else 0
                    ),
                    2,
                ),
            }
            for row in rows
        ]

    def search_tickers(self, query: str) -> List[Ticker]:
        """Search tickers by symbol or description"""
        search_query = """
            SELECT * FROM tickers
            WHERE symbol ILIKE ? OR description ILIKE ?
            ORDER BY
                CASE WHEN symbol ILIKE ? THEN 1 ELSE 2 END,
                symbol
        """

        search_term = f"%{query}%"
        exact_term = f"{query}%"

        rows = self.db.fetchall(search_query, [search_term, search_term, exact_term])

        return [
            Ticker(
                id=row[0],
                symbol=row[1],
                description=row[2],
                product_category=row[3],
                is_custom=bool(row[4]),
                created_at=row[5],
                updated_at=row[6],
            )
            for row in rows
        ]
