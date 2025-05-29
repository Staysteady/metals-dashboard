#!/usr/bin/env python3
"""Test Bloomberg API connectivity"""

import sys
import os

print("=== Bloomberg API Test ===")

# Test 1: Try importing blpapi
print("\n1. Testing blpapi import...")
try:
    import blpapi
    print("✅ SUCCESS: blpapi imported successfully")
    if hasattr(blpapi, '__version__'):
        print(f"   Version: {blpapi.__version__}")
    else:
        print("   Version: Unknown")
except ImportError as e:
    print(f"❌ FAILED: blpapi not available - {e}")
    print("   Bloomberg Python API is not installed or not in Python path")

# Test 2: Check Bloomberg API installation paths
print("\n2. Checking Bloomberg installation paths...")
bloomberg_paths = [
    "C:\\blp\\API",
    "C:\\blp\\API\\APIv3",
    "C:\\blp\\API\\Office Tools",
    "C:\\Program Files\\Bloomberg"
]

for path in bloomberg_paths:
    if os.path.exists(path):
        print(f"✅ Found: {path}")
        try:
            files = os.listdir(path)
            python_files = [f for f in files if 'python' in f.lower() or f.endswith('.dll')]
            if python_files:
                print(f"   Python-related files: {python_files}")
        except PermissionError:
            print("   (Permission denied to list contents)")
    else:
        print(f"❌ Not found: {path}")

# Test 3: Check if Bloomberg Terminal is running
print("\n3. Testing Bloomberg Terminal connection...")
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
except Exception as e:
    print(f"❌ Error testing Bloomberg port: {e}")

print("\n=== Test Complete ===") 