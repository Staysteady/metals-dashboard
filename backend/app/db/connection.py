import logging
from pathlib import Path
from typing import Any, List, Optional

import duckdb

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """DuckDB database connection manager"""

    def __init__(self, db_path: str = "./data/metals.db") -> None:
        self.db_path = db_path
        self._connection: Optional[duckdb.DuckDBPyConnection] = None
        self._ensure_data_directory()

    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists"""
        data_dir = Path(self.db_path).parent
        data_dir.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection"""
        if self._connection is None:
            self._connection = duckdb.connect(self.db_path)
            logger.info(f"Connected to DuckDB at {self.db_path}")
        return self._connection

    def close(self) -> None:
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def execute(self, query: str, parameters: Optional[List[Any]] = None) -> Any:
        """Execute a query"""
        conn = self.get_connection()
        if parameters:
            return conn.execute(query, parameters)
        return conn.execute(query)

    def fetchall(self, query: str, parameters: Optional[List[Any]] = None) -> Any:
        """Execute query and fetch all results"""
        result = self.execute(query, parameters)
        return result.fetchall()

    def fetchone(self, query: str, parameters: Optional[List[Any]] = None) -> Any:
        """Execute query and fetch one result"""
        result = self.execute(query, parameters)
        return result.fetchone()


# Global database instance
db = DatabaseConnection()


def get_db() -> DatabaseConnection:
    """Get database instance"""
    return db


def init_database() -> None:
    """Initialize database with required tables"""
    conn = db.get_connection()

    # Create tickers table with primary key
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tickers (
            id INTEGER PRIMARY KEY,
            symbol VARCHAR NOT NULL UNIQUE,
            description VARCHAR NOT NULL,
            product_category VARCHAR NOT NULL,
            is_custom BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """
    )

    # Create price_data table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS price_data (
            id BIGINT PRIMARY KEY,
            ticker_id INTEGER NOT NULL,
            symbol VARCHAR NOT NULL,
            date TIMESTAMP NOT NULL,
            px_last DOUBLE NOT NULL,
            px_open DOUBLE,
            px_high DOUBLE,
            px_low DOUBLE,
            px_volume DOUBLE,
            UNIQUE(ticker_id, date)
        )
    """
    )

    # Create custom_instruments table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS custom_instruments (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL UNIQUE,
            type VARCHAR NOT NULL,
            definition JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """
    )

    # Create settlement_prices table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settlement_prices (
            id BIGINT PRIMARY KEY,
            symbol VARCHAR NOT NULL,
            date TIMESTAMP NOT NULL,
            settlement_price DOUBLE NOT NULL,
            product_category VARCHAR NOT NULL,
            UNIQUE(symbol, date)
        )
    """
    )

    logger.info("Database tables initialized successfully")


def health_check() -> dict:
    """Perform database health check"""
    try:
        conn = db.get_connection()

        # Test basic connectivity
        result = conn.execute("SELECT 1 as test").fetchone()
        if result is None or result[0] != 1:
            return {"status": "error", "message": "Basic query failed"}

        # Check if tables exist
        tables = conn.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main'
        """
        ).fetchall()

        table_names = [table[0] for table in tables]
        required_tables = [
            "tickers",
            "price_data",
            "custom_instruments",
            "settlement_prices",
        ]
        missing_tables = [
            table for table in required_tables if table not in table_names
        ]

        if missing_tables:
            return {
                "status": "warning",
                "message": f"Missing tables: {', '.join(missing_tables)}",
            }

        # Check data counts
        ticker_result = conn.execute("SELECT COUNT(*) FROM tickers").fetchone()
        price_result = conn.execute("SELECT COUNT(*) FROM price_data").fetchone()

        ticker_count = ticker_result[0] if ticker_result else 0
        price_count = price_result[0] if price_result else 0

        return {
            "status": "healthy",
            "message": "Database is operational",
            "data": {
                "tables": len(table_names),
                "tickers": ticker_count,
                "price_records": price_count,
            },
        }

    except Exception as e:
        return {"status": "error", "message": f"Database error: {str(e)}"}


def cleanup_old_data(days: int = 90) -> int:
    """Clean up old price data beyond specified days"""
    try:
        conn = db.get_connection()

        result = conn.execute(
            """
            DELETE FROM price_data
            WHERE date < (CURRENT_DATE - INTERVAL ? DAYS)
        """,
            [days],
        )

        rows_deleted = result.rowcount if hasattr(result, "rowcount") else 0
        logger.info(f"Cleaned up {rows_deleted} old price records")

        return rows_deleted

    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        return 0
