#!/usr/bin/env python3
"""Test xbbg Bloomberg API connectivity"""

import sys
import os
import traceback

print("=== xbbg Bloomberg API Test ===")

# Test 1: Try importing xbbg
print("\n1. Testing xbbg import...")
try:
    from xbbg import blp
    print("✅ SUCCESS: xbbg imported successfully")
except ImportError as e:
    print(f"❌ FAILED: xbbg not available - {e}")
    sys.exit(1)

# Test 2: Check Bloomberg Terminal connectivity
print("\n2. Testing Bloomberg Terminal connection...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8194))
    sock.close()
    
    if result == 0:
        print("✅ Bloomberg Terminal API port 8194 is accessible")
        print("   Bloomberg Terminal appears to be running")
    else:
        print("❌ Bloomberg Terminal API port 8194 is NOT accessible")
        print("   Bloomberg Terminal may not be running or API not enabled")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error testing Bloomberg port: {e}")
    sys.exit(1)

# Test 3: Try a simple Bloomberg data request
print("\n3. Testing xbbg data request...")
try:
    # Try to get a simple piece of data - current price of a well-known ticker
    print("   Requesting last price for AAPL US Equity...")
    result = blp.bdp(tickers='AAPL US Equity', flds=['px_last'])
    print(f"✅ SUCCESS: Got data from Bloomberg!")
    print(f"   Result: {result}")
    
    # Test if we can get the copper ticker that was added
    print("\n   Requesting last price for LMCADS03 Comdty...")
    copper_result = blp.bdp(tickers='LMCADS03 Comdty', flds=['px_last', 'security_name'])
    print(f"✅ SUCCESS: Got copper data from Bloomberg!")
    print(f"   Result: {copper_result}")
    
except Exception as e:
    print(f"❌ FAILED: Bloomberg data request failed - {e}")
    print("   Full error details:")
    traceback.print_exc()

print("\n=== Test Complete ===") 