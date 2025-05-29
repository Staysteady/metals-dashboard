import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestPricesAPI:
    """Test prices API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_get_latest_prices_default(self, client):
        """Test getting latest prices with default symbols"""
        response = client.get("/prices/latest")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 6  # Default metals count

        for item in data:
            assert "symbol" in item
            assert "description" in item
            assert "product_category" in item
            assert "px_last" in item
            assert "change" in item
            assert "change_pct" in item
            assert "timestamp" in item

    def test_get_latest_prices_with_precious(self, client):
        """Test getting latest prices including precious metals"""
        response = client.get("/prices/latest?include_precious=true")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10  # Base metals + precious metals

    def test_get_latest_prices_custom_symbols(self, client):
        """Test getting latest prices with custom symbols"""
        response = client.get("/prices/latest?symbols=LMCADS03,XAU=")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        symbols = [item["symbol"] for item in data]
        assert "LMCADS03" in symbols
        assert "XAU=" in symbols

    def test_get_historical_prices(self, client):
        """Test getting historical prices"""
        response = client.get("/prices/historical/LMCADS03?days=7")
        assert response.status_code == 200

        data = response.json()
        assert "symbol" in data
        assert data["symbol"] == "LMCADS03"
        assert "data_points" in data
        assert "start_date" in data
        assert "end_date" in data

        assert len(data["data_points"]) == 8  # 7 days + 1

        for point in data["data_points"]:
            assert "date" in point
            assert "price" in point

    def test_get_historical_prices_invalid_days(self, client):
        """Test historical prices with invalid days parameter"""
        response = client.get("/prices/historical/LMCADS03?days=400")
        assert response.status_code == 422  # Validation error

    def test_get_market_status(self, client):
        """Test getting market status"""
        response = client.get("/prices/market-status")
        assert response.status_code == 200

        data = response.json()
        assert "is_open" in data
        assert "message" in data
        assert isinstance(data["is_open"], bool)

        # Should have either next_open or next_close
        assert "next_open" in data or "next_close" in data

    def test_get_available_symbols(self, client):
        """Test getting available symbols"""
        response = client.get("/prices/symbols")
        assert response.status_code == 200

        data = response.json()
        assert "base_metals" in data
        assert "precious_metals" in data

        assert len(data["base_metals"]) == 6
        assert len(data["precious_metals"]) == 4

        # Check structure
        for metal in data["base_metals"]:
            assert "symbol" in metal
            assert "description" in metal
            assert "category" in metal
