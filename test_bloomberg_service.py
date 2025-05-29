#!/usr/bin/env python3
"""Test the updated Bloomberg service with real API"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from app.services.bloomberg_service import BloombergService

def test_bloomberg_service():
    print("=== Testing Bloomberg Service ===")
    
    # Create service instance
    service = BloombergService()
    
    print(f"✅ Service created")
    print(f"   Use dummy data: {service.get_current_use_dummy_data()}")
    print(f"   Bloomberg available: {service.BLOOMBERG_AVAILABLE}")
    print(f"   Connected: {service.is_connected}")
    
    if not service.BLOOMBERG_AVAILABLE:
        print("❌ Bloomberg API not available")
        return False
    
    # Test with some sample tickers
    test_symbols = [
        "AAPL US Equity",
        "MSFT US Equity", 
        "LMCADS03 Comdty",  # LME Copper 3M
        "GC1 Comdty"       # Gold Front Month
    ]
    
    print(f"\n📊 Testing real-time data for: {test_symbols}")
    
    try:
        data = service.get_real_time_data(test_symbols)
        
        print(f"✅ Retrieved data for {len(data)} symbols:")
        for item in data:
            symbol = item.get('symbol', 'Unknown')
            price = item.get('px_last', 'N/A')
            change = item.get('change', 'N/A')
            description = item.get('description', '')
            category = item.get('product_category', '')
            
            print(f"   {symbol}: ${price} ({change:+.2f}) - {description} [{category}]" 
                  if isinstance(price, (int, float)) and isinstance(change, (int, float))
                  else f"   {symbol}: ${price} ({change}) - {description} [{category}]")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing real-time data: {e}")
        return False
    
    finally:
        service.close()

if __name__ == "__main__":
    success = test_bloomberg_service()
    sys.exit(0 if success else 1) 