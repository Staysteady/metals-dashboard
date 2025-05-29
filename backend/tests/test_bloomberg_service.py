import pytest
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.services.bloomberg_service import BloombergService


class TestBloombergService:
    """Test Bloomberg service functionality"""

    @pytest.fixture
    def mock_bloomberg_available(self):
        """Mock Bloomberg API as available"""
        with patch('app.services.bloomberg_service.BLOOMBERG_AVAILABLE', True):
            with patch('app.services.bloomberg_service.blpapi') as mock_blpapi:
                # Mock session and service
                mock_session = MagicMock()
                mock_session.start.return_value = True
                mock_session.openService.return_value = True
                mock_blpapi.Session.return_value = mock_session
                mock_blpapi.SessionOptions.return_value = MagicMock()
                
                yield mock_blpapi, mock_session

    def test_service_initialization_with_bloomberg(self, mock_bloomberg_available):
        """Test service initializes with Bloomberg API"""
        mock_blpapi, mock_session = mock_bloomberg_available
        
        service = BloombergService()
        
        assert service._is_connected is True
        mock_session.start.assert_called_once()
        mock_session.openService.assert_called_once_with("//blp/refdata")

    def test_service_initialization_without_bloomberg(self):
        """Test service fails to initialize without Bloomberg API"""
        with patch('app.services.bloomberg_service.BLOOMBERG_AVAILABLE', False):
            with pytest.raises(RuntimeError, match="Bloomberg API is required"):
                BloombergService()

    def test_get_connection_status_connected(self, mock_bloomberg_available):
        """Test connection status when connected"""
        mock_blpapi, mock_session = mock_bloomberg_available
        
        service = BloombergService()
        status = service.get_connection_status()
        
        assert status['bloomberg_available'] is True
        assert status['is_connected'] is True
        assert status['status'] == 'connected'
        assert 'Connected to Bloomberg Terminal' in status['message']

    def test_get_connection_status_disconnected(self):
        """Test connection status when Bloomberg unavailable"""
        with patch('app.services.bloomberg_service.BLOOMBERG_AVAILABLE', False):
            # Create service instance that will fail
            try:
                service = BloombergService()
            except RuntimeError:
                # Expected to fail, create a mock service for testing status
                service = BloombergService.__new__(BloombergService)
                service._is_connected = False
                
                status = service.get_connection_status()
                
                assert status['bloomberg_available'] is False
                assert status['is_connected'] is False
                assert status['status'] == 'disconnected'

    def test_get_real_time_data_success(self, mock_bloomberg_available):
        """Test getting real-time data successfully"""
        mock_blpapi, mock_session = mock_bloomberg_available
        
        # Mock Bloomberg response
        mock_event = MagicMock()
        mock_event.eventType.return_value = mock_blpapi.Event.RESPONSE
        
        mock_msg = MagicMock()
        mock_msg.hasElement.return_value = True
        
        mock_security_data = MagicMock()
        mock_security_data.numValues.return_value = 1
        
        mock_security = MagicMock()
        mock_security.getElementAsString.return_value = "LMCADS03 COMDTY"
        mock_security.hasElement.return_value = False  # No security errors
        
        mock_field_data = MagicMock()
        mock_field_data.hasElement.return_value = True
        mock_field_data.getElement.return_value.isNull.return_value = False
        mock_field_data.getElementAsFloat.return_value = 9568.0
        mock_field_data.getElementAsString.return_value = "Copper 3 Month"
        
        mock_security.getElement.return_value = mock_field_data
        mock_security_data.getValueAsElement.return_value = mock_security
        mock_msg.getElement.return_value = mock_security_data
        
        mock_event.__iter__ = lambda self: iter([mock_msg])
        mock_session.nextEvent.return_value = mock_event
        
        service = BloombergService()
        result = service.get_real_time_data(["LMCADS03 COMDTY"])
        
        assert len(result) == 1
        assert result[0]['symbol'] == "LMCADS03 COMDTY"
        assert result[0]['px_last'] == 9568.0

    def test_get_real_time_data_connection_failure(self, mock_bloomberg_available):
        """Test handling connection failure during real-time data fetch"""
        mock_blpapi, mock_session = mock_bloomberg_available
        
        service = BloombergService()
        service._is_connected = False  # Simulate disconnection
        
        # Should attempt to reconnect but fail
        with patch.object(service, '_initialize_bloomberg') as mock_init:
            mock_init.side_effect = RuntimeError("Connection failed")
            
            result = service.get_real_time_data(["LMCADS03 COMDTY"])
            
            assert result == []
            mock_init.assert_called_once()

    def test_get_historical_data_success(self, mock_bloomberg_available):
        """Test getting historical data successfully"""
        mock_blpapi, mock_session = mock_bloomberg_available
        
        # Mock Bloomberg historical response
        mock_event = MagicMock()
        mock_event.eventType.return_value = mock_blpapi.Event.RESPONSE
        
        mock_msg = MagicMock()
        mock_msg.hasElement.return_value = True
        
        mock_security_data = MagicMock()
        mock_security_data.hasElement.return_value = True
        
        mock_field_data = MagicMock()
        mock_field_data.numValues.return_value = 2
        
        # Mock data points
        mock_data_point1 = MagicMock()
        mock_data_point1.hasElement.return_value = True
        mock_data_point1.getElementAsDatetime.return_value = datetime(2024, 1, 1)
        mock_data_point1.getElementAsFloat.return_value = 9500.0
        
        mock_data_point2 = MagicMock()
        mock_data_point2.hasElement.return_value = True
        mock_data_point2.getElementAsDatetime.return_value = datetime(2024, 1, 2)
        mock_data_point2.getElementAsFloat.return_value = 9550.0
        
        mock_field_data.getValueAsElement.side_effect = [mock_data_point1, mock_data_point2]
        mock_security_data.getElement.return_value = mock_field_data
        mock_msg.getElement.return_value = mock_security_data
        
        mock_event.__iter__ = lambda self: iter([mock_msg])
        mock_session.nextEvent.return_value = mock_event
        
        service = BloombergService()
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)
        
        result = service.get_historical_data("LMCADS03 COMDTY", start_date, end_date)
        
        assert len(result) == 2
        assert result[0]['date'] == '2024-01-01'
        assert result[0]['price'] == 9500.0
        assert result[1]['date'] == '2024-01-02'
        assert result[1]['price'] == 9550.0

    def test_close_connection(self, mock_bloomberg_available):
        """Test closing Bloomberg connection"""
        mock_blpapi, mock_session = mock_bloomberg_available
        
        service = BloombergService()
        service.close()
        
        mock_session.stop.assert_called_once()
