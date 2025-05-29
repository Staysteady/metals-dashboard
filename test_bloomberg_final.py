#!/usr/bin/env python3
"""Test Bloomberg API connectivity with properly installed blpapi"""

import sys
import os
import traceback
import time

print("=== Bloomberg API Final Test ===")

# Test 1: Import Bloomberg API
print("\n1. Testing Bloomberg API import...")
try:
    import blpapi
    print("✅ SUCCESS: blpapi imported successfully")
    print(f"   Bloomberg API version: {blpapi.__version__}")
except ImportError as e:
    print(f"❌ FAILED: blpapi not available - {e}")
    sys.exit(1)

# Test 2: Test Bloomberg Terminal connectivity
print("\n2. Testing Bloomberg Terminal connectivity...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8194))
    sock.close()
    
    if result == 0:
        print("✅ Bloomberg Terminal API port 8194 is accessible")
    else:
        print("❌ Bloomberg Terminal API port 8194 is NOT accessible")
        print("   Please ensure Bloomberg Terminal is running")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error testing Bloomberg port: {e}")
    sys.exit(1)

# Test 3: Create Bloomberg session
print("\n3. Testing Bloomberg API session creation...")
try:
    # Session options
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost("localhost")
    sessionOptions.setServerPort(8194)
    
    # Create session
    session = blpapi.Session(sessionOptions)
    
    if session.start():
        print("✅ Bloomberg session started successfully")
        
        # Open reference data service
        if session.openService("//blp/refdata"):
            print("✅ Reference data service opened successfully")
            service = session.getService("//blp/refdata")
            
            # Test 4: Request sample data
            print("\n4. Testing sample data request...")
            
            # Create request for reference data
            request = service.createRequest("ReferenceDataRequest")
            request.append("securities", "AAPL US Equity")
            request.append("securities", "IBM US Equity")
            request.append("fields", "PX_LAST")
            request.append("fields", "NAME")
            
            # Send request
            print("   Sending request for AAPL and IBM prices...")
            session.sendRequest(request)
            
            # Process response
            timeout_seconds = 10
            start_time = time.time()
            
            while True:
                event = session.nextEvent(100)  # 100ms timeout
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    print("✅ Received response from Bloomberg!")
                    
                    for msg in event:
                        print(f"   Response: {msg}")
                        
                        # Extract securities data
                        securities = msg.getElement("securityData")
                        for i in range(securities.numValues()):
                            security = securities.getValue(i)
                            ticker = security.getElement("security").getValue()
                            
                            if security.hasElement("fieldData"):
                                fieldData = security.getElement("fieldData")
                                
                                if fieldData.hasElement("PX_LAST"):
                                    price = fieldData.getElement("PX_LAST").getValue()
                                    print(f"   {ticker}: ${price}")
                                
                                if fieldData.hasElement("NAME"):
                                    name = fieldData.getElement("NAME").getValue()
                                    print(f"   {ticker}: {name}")
                    
                    break
                    
                elif event.eventType() == blpapi.Event.TIMEOUT:
                    if time.time() - start_time > timeout_seconds:
                        print(f"❌ Request timed out after {timeout_seconds} seconds")
                        break
                        
                elif event.eventType() == blpapi.Event.REQUEST_STATUS:
                    for msg in event:
                        print(f"   Request status: {msg}")
            
            session.stop()
            print("✅ Session closed successfully")
            
        else:
            print("❌ Failed to open reference data service")
            session.stop()
            sys.exit(1)
    else:
        print("❌ Failed to start Bloomberg session")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error during Bloomberg API test: {e}")
    print(f"   Traceback: {traceback.format_exc()}")
    sys.exit(1)

print("\n🎉 All Bloomberg API tests passed successfully!")
print("   You can now use live Bloomberg data in your application!") 