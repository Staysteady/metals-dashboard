import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List

from ..db.connection import get_db

logger = logging.getLogger(__name__)


def generate_dummy_tickers() -> List[Dict]:
    """Generate common metals tickers with realistic Bloomberg symbols"""
    tickers = [
        # Aluminum
        {
            "symbol": "LMAHDS03",
            "description": "LME Aluminum 3M",
            "product_category": "AH",
        },
        {
            "symbol": "LMAHDS01",
            "description": "LME Aluminum Cash",
            "product_category": "AH",
        },
        {
            "symbol": "LMAHDS15",
            "description": "LME Aluminum 15M",
            "product_category": "AH",
        },
        # Copper
        {
            "symbol": "LMCADS03",
            "description": "LME Copper 3M",
            "product_category": "CA",
        },
        {
            "symbol": "LMCADS01",
            "description": "LME Copper Cash",
            "product_category": "CA",
        },
        {
            "symbol": "LMCADS15",
            "description": "LME Copper 15M",
            "product_category": "CA",
        },
        # Zinc
        {"symbol": "LMZSDS03", "description": "LME Zinc 3M", "product_category": "ZN"},
        {
            "symbol": "LMZSDS01",
            "description": "LME Zinc Cash",
            "product_category": "ZN",
        },
        {"symbol": "LMZSDS15", "description": "LME Zinc 15M", "product_category": "ZN"},
        # Lead
        {"symbol": "LMPBDS03", "description": "LME Lead 3M", "product_category": "PB"},
        {
            "symbol": "LMPBDS01",
            "description": "LME Lead Cash",
            "product_category": "PB",
        },
        {"symbol": "LMPBDS15", "description": "LME Lead 15M", "product_category": "PB"},
        # Nickel
        {
            "symbol": "LMNIDS03",
            "description": "LME Nickel 3M",
            "product_category": "NI",
        },
        {
            "symbol": "LMNIDS01",
            "description": "LME Nickel Cash",
            "product_category": "NI",
        },
        {
            "symbol": "LMNIDS15",
            "description": "LME Nickel 15M",
            "product_category": "NI",
        },
        # Tin
        {"symbol": "LMSNDS03", "description": "LME Tin 3M", "product_category": "SN"},
        {"symbol": "LMSNDS01", "description": "LME Tin Cash", "product_category": "SN"},
        {"symbol": "LMSNDS15", "description": "LME Tin 15M", "product_category": "SN"},
    ]

    return tickers


def get_base_price(product_category: str) -> float:
    """Get realistic base prices for different metals (USD per tonne)"""
    base_prices = {
        "AH": 2200.0,  # Aluminum ~$2200/tonne
        "CA": 8500.0,  # Copper ~$8500/tonne
        "ZN": 2800.0,  # Zinc ~$2800/tonne
        "PB": 2100.0,  # Lead ~$2100/tonne
        "NI": 18000.0,  # Nickel ~$18000/tonne
        "SN": 32000.0,  # Tin ~$32000/tonne
    }
    return base_prices.get(product_category, 1000.0)


def generate_price_series(
    ticker_id: int,
    symbol: str,
    product_category: str,
    start_date: datetime,
    days: int = 180,
) -> List[Dict]:
    """Generate realistic price series with volatility and trends"""
    prices = []
    base_price = get_base_price(product_category)
    current_price = base_price

    # Volatility parameters by metal
    volatility = {
        "AH": 0.02,  # 2% daily volatility
        "CA": 0.025,  # 2.5% daily volatility
        "ZN": 0.03,  # 3% daily volatility
        "PB": 0.025,  # 2.5% daily volatility
        "NI": 0.04,  # 4% daily volatility (more volatile)
        "SN": 0.035,  # 3.5% daily volatility
    }.get(product_category, 0.025)

    for i in range(days):
        date = start_date + timedelta(days=i)

        # Skip weekends (basic approximation)
        if date.weekday() >= 5:
            continue

        # Generate daily price movement
        daily_change = random.gauss(0, volatility)
        current_price *= 1 + daily_change

        # Add some mean reversion to keep prices realistic
        if current_price > base_price * 1.3:
            current_price *= 0.99
        elif current_price < base_price * 0.7:
            current_price *= 1.01

        # Generate OHLC data
        px_open = current_price * (1 + random.gauss(0, 0.005))
        px_high = max(px_open, current_price) * (1 + abs(random.gauss(0, 0.01)))
        px_low = min(px_open, current_price) * (1 - abs(random.gauss(0, 0.01)))
        px_volume = random.uniform(1000, 10000)

        prices.append(
            {
                "ticker_id": ticker_id,
                "symbol": symbol,
                "date": date,
                "px_last": round(current_price, 2),
                "px_open": round(px_open, 2),
                "px_high": round(px_high, 2),
                "px_low": round(px_low, 2),
                "px_volume": round(px_volume, 0),
            }
        )

    return prices


def populate_dummy_data() -> None:
    """Populate database with dummy tickers and price data"""
    db = get_db()
    conn = db.get_connection()

    try:
        # Check if data already exists
        ticker_result = conn.execute("SELECT COUNT(*) FROM tickers").fetchone()
        ticker_count = ticker_result[0] if ticker_result else 0

        if ticker_count > 0:
            logger.info(
                f"Database already contains {ticker_count} tickers, skipping dummy data generation"
            )
            return

        logger.info("Generating dummy data...")

        # Insert default settings
        conn.execute(
            """
            INSERT INTO settings (id, use_dummy_data, polling_interval_minutes, theme, database_path)
            VALUES (1, TRUE, 15, 'light', './data/metals.db')
        """
        )

        # Generate and insert tickers
        tickers = generate_dummy_tickers()
        for i, ticker in enumerate(tickers, 1):
            conn.execute(
                """
                INSERT INTO tickers (id, symbol, description, product_category, is_custom)
                VALUES (?, ?, ?, ?, FALSE)
            """,
                (
                    i,
                    ticker["symbol"],
                    ticker["description"],
                    ticker["product_category"],
                ),
            )

        logger.info(f"Inserted {len(tickers)} tickers")

        # Generate price data for each ticker
        start_date = datetime.now() - timedelta(days=180)

        ticker_rows = conn.execute(
            "SELECT id, symbol, product_category FROM tickers"
        ).fetchall()
        total_prices = 0
        price_id = 1

        for ticker_id, symbol, product_category in ticker_rows:
            prices = generate_price_series(
                ticker_id, symbol, product_category, start_date
            )

            for price in prices:
                conn.execute(
                    """
                    INSERT INTO price_data (id, ticker_id, symbol, date, px_last, px_open, px_high, px_low, px_volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        price_id,
                        price["ticker_id"],
                        price["symbol"],
                        price["date"],
                        price["px_last"],
                        price["px_open"],
                        price["px_high"],
                        price["px_low"],
                        price["px_volume"],
                    ),
                )
                price_id += 1

            total_prices += len(prices)

        # Generate settlement prices (latest prices as settlements)
        latest_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        settlement_id = 1
        for ticker_id, symbol, product_category in ticker_rows:
            latest_price = conn.execute(
                """
                SELECT px_last FROM price_data
                WHERE ticker_id = ?
                ORDER BY date DESC
                LIMIT 1
            """,
                (ticker_id,),
            ).fetchone()

            if latest_price:
                conn.execute(
                    """
                    INSERT INTO settlement_prices (id, symbol, date, settlement_price, product_category)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        settlement_id,
                        symbol,
                        latest_date,
                        latest_price[0],
                        product_category,
                    ),
                )
                settlement_id += 1

        logger.info(f"Generated {total_prices} price records and settlement prices")
        logger.info("Dummy data population completed successfully")

    except Exception as e:
        logger.error(f"Error populating dummy data: {e}")
        raise


def add_custom_instruments_examples() -> None:
    """Add example custom instruments"""
    db = get_db()
    conn = db.get_connection()

    try:
        # Check if custom instruments already exist
        existing_result = conn.execute(
            "SELECT COUNT(*) FROM custom_instruments"
        ).fetchone()
        existing_count = existing_result[0] if existing_result else 0

        if existing_count > 0:
            logger.info(
                f"Database already contains {existing_count} custom instruments, skipping custom instruments generation"
            )
            return

        # Zinc-Lead spread example
        zn_lead_spread = {
            "type": "switch",
            "base_symbol": "LMZSDS03",
            "quote_symbol": "LMPBDS03",
            "operation": "subtract",
            "description": "Zinc 3M minus Lead 3M spread",
        }

        conn.execute(
            """
            INSERT INTO custom_instruments (id, name, type, definition)
            VALUES (?, ?, ?, ?)
        """,
            (1, "ZN-PB Spread", "switch", json.dumps(zn_lead_spread)),
        )

        # Metals index example
        metals_index = {
            "type": "weighted_index",
            "components": [
                {"symbol": "LMCADS03", "weight": 0.4},  # 40% Copper
                {"symbol": "LMAHDS03", "weight": 0.3},  # 30% Aluminum
                {"symbol": "LMZSDS03", "weight": 0.2},  # 20% Zinc
                {"symbol": "LMNIDS03", "weight": 0.1},  # 10% Nickel
            ],
            "base_value": 100.0,
            "description": "Base metals weighted index",
        }

        conn.execute(
            """
            INSERT INTO custom_instruments (id, name, type, definition)
            VALUES (?, ?, ?, ?)
        """,
            (2, "Base Metals Index", "weighted_index", json.dumps(metals_index)),
        )

        logger.info("Added example custom instruments")

    except Exception as e:
        logger.error(f"Error adding custom instruments: {e}")
        raise
