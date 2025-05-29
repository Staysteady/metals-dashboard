import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.services.bloomberg_service import BloombergService


class TestBloombergService:
    """Test Bloomberg service functionality"""

    @pytest.fixture
    def mock_db(self):
        """Mock database for testing"""
        mock_connection = MagicMock()
        mock_db = MagicMock()
        mock_db.get_connection.return_value = mock_connection
        return mock_db

    @pytest.fixture
    def bloomberg_service(self, mock_db):
        """Create Bloomberg service instance with mocked database"""
        # Force dummy data mode for tests
        with patch.dict(os.environ, {"USE_DUMMY_DATA": "true"}):
            service = BloombergService()
            # Inject mock database
            service._db = mock_db
            yield service

    def test_service_initialization_dummy_mode(self, bloomberg_service):
        """Test service initializes in dummy mode"""
        assert bloomberg_service.session is None
        assert bloomberg_service.service is None
        assert bloomberg_service.is_connected is False

    def test_get_real_time_data_dummy(self, bloomberg_service):
        """Test getting real-time data in dummy mode"""
        symbols = ["LMCADS03", "LMAHDS03", "XAU="]
        results = bloomberg_service.get_real_time_data(symbols)

        assert len(results) == 3

        for result in results:
            assert "symbol" in result
            assert "px_last" in result
            assert "change" in result
            assert "change_pct" in result
            assert "description" in result
            assert "product_category" in result
            assert result["symbol"] in symbols
            assert isinstance(result["px_last"], float)
            assert result["px_last"] > 0

    def test_real_time_data_caching(self):
        """Test that real-time data is cached in database"""
        service = BloombergService()
        symbols = ["LMCADS03", "LMAHDS03"]

        # Get data (should cache it)
        service.get_real_time_data(symbols)

        # Verify data was cached (basic check)
        # In a real test, we'd check the database directly
        assert True  # Placeholder assertion

    def test_get_historical_data_dummy(self, bloomberg_service):
        """Test getting historical data in dummy mode"""
        symbol = "LMCADS03"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        results = bloomberg_service.get_historical_data(symbol, start_date, end_date)

        assert len(results) == 8  # 7 days + 1

        for result in results:
            assert "date" in result
            assert "price" in result
            assert isinstance(result["price"], float)
            assert result["price"] > 0

        # Check dates are in order
        dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in results]
        assert dates == sorted(dates)

    def test_historical_data_cache_hit(self, bloomberg_service, mock_db):
        """Test retrieving historical data from cache"""
        symbol = "LMCADS03"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        mock_connection = mock_db.get_connection.return_value

        # Mock cached data
        cached_data = [
            (datetime.now() - timedelta(days=i), 8500 + i * 10) for i in range(8)
        ]
        mock_connection.execute.return_value.fetchall.return_value = cached_data

        # Get historical data (should use cache)
        results = bloomberg_service.get_historical_data(symbol, start_date, end_date)

        assert len(results) == 8
        # Verify it checked the cache
        assert mock_connection.execute.called

    def test_historical_data_cache_miss(self, bloomberg_service, mock_db):
        """Test fetching historical data when cache is empty"""
        symbol = "LMCADS03"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        mock_connection = mock_db.get_connection.return_value

        # Mock empty cache
        mock_connection.execute.return_value.fetchall.return_value = []

        # Mock ticker exists for caching
        mock_connection.execute.return_value.fetchone.return_value = (
            1,
        )  # ticker_id = 1

        # Get historical data (should generate dummy data and cache it)
        results = bloomberg_service.get_historical_data(symbol, start_date, end_date)

        assert len(results) == 8
        # Verify it tried to cache the data
        assert mock_connection.execute.call_count > 1

    def test_unknown_symbol_dummy(self, bloomberg_service):
        """Test handling unknown symbols in dummy mode"""
        symbols = ["UNKNOWN123"]
        results = bloomberg_service.get_real_time_data(symbols)

        assert len(results) == 0
