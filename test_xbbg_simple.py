#!/usr/bin/env python3
"""Test xbbg Bloomberg API with graceful fallback"""

import os
import sys

print("=== xbbg Simple Test ===")

# Test 1: Test terminal connectivity first
print("\n1. Testing Bloomberg Terminal connectivity...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8194))
    sock.close()
    
    if result == 0:
        print("✅ Bloomberg Terminal API port 8194 is accessible")
    else:
        print("❌ Bloomberg Terminal API port 8194 is NOT accessible")
        print("   Bloomberg Terminal may not be running or API not enabled")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error testing Bloomberg port: {e}")
    sys.exit(1)

# Test 2: Try to create a mock blpapi to bypass the import error
print("\n2. Creating mock blpapi module...")
try:
    import types
    import sys
    
    # Create a mock blpapi module
    mock_blpapi = types.ModuleType('blpapi')
    
    # Add basic classes and functions that xbbg might need
    mock_blpapi.Session = lambda *args, **kwargs: None
    mock_blpapi.SessionOptions = lambda *args, **kwargs: None
    mock_blpapi.Event = lambda *args, **kwargs: None
    
    # Add to sys.modules so import blpapi will find our mock
    sys.modules['blpapi'] = mock_blpapi
    print("✅ Mock blpapi module created")
    
except Exception as e:
    print(f"❌ Error creating mock blpapi: {e}")
    sys.exit(1)

# Test 3: Try importing xbbg with our mock
print("\n3. Testing xbbg import with mock blpapi...")
try:
    from xbbg import blp
    print("✅ SUCCESS: xbbg imported with mock blpapi")
except Exception as e:
    print(f"❌ FAILED: xbbg import failed even with mock - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Try a simple data request (will likely fail but let's see how)
print("\n4. Testing xbbg data request...")
try:
    result = blp.bdp(tickers='AAPL US Equity', flds=['px_last'])
    print(f"✅ SUCCESS: Got data from xbbg!")
    print(f"   Result: {result}")
    
except Exception as e:
    print(f"❌ Expected failure: xbbg data request failed - {e}")
    print("   This is expected since we're using a mock blpapi")

print("\n=== Test Complete ===")
print("Results:")
print("- Bloomberg Terminal is running and accessible")
print("- xbbg can be imported with mock blpapi")
print("- Data requests will fail without real Bloomberg API")
print("\nConclusion: The issue is that xbbg requires the full Bloomberg Python API (blpapi)")
print("which is not publicly available and requires special Bloomberg licensing.") 