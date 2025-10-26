#!/usr/bin/env python3
"""
Test script for Dexcom integration
This script tests the Dexcom tools via share
"""

import os
import sys
from dotenv import load_dotenv
import pytest

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

def test_dexcom_tools():
    """Test the Dexcom integration tools"""
    print("Testing Dexcom Integration...")

    # Check if credentials are configured
    username = os.getenv('DEXCOM_USERNAME')
    password = os.getenv('DEXCOM_PASSWORD')
    region = os.getenv('DEXCOM_REGION', 'us')

    if not username or not password:
        pytest.skip("Dexcom credentials not configured; skipping integration test")

    print(f" Credentials found: {username} (region: {region})")

    # Test pydexcom directly
    from pydexcom import Dexcom

    print("\nTesting Dexcom connection...")
    dexcom = Dexcom(username=username, password=password, region=region)
    assert dexcom is not None

    print("Testing get_current_glucose_reading()...")
    glucose_reading = dexcom.get_current_glucose_reading()
    # Allow None; just ensure no exception and type consistency when present
    if glucose_reading:
        assert hasattr(glucose_reading, 'value')

    print("\nTesting get_latest_glucose_reading()...")
    latest_reading = dexcom.get_latest_glucose_reading()
    if latest_reading:
        assert hasattr(latest_reading, 'value')

    print("\nTesting get_glucose_readings(minutes=60)...")
    glucose_readings = dexcom.get_glucose_readings(minutes=60)
    if glucose_readings:
        assert isinstance(glucose_readings, list)

if __name__ == "__main__":
    success = test_dexcom_tools()
    if success:
        print("\n Dexcom integration test completed!")
    else:
        print("\nDexcom integration test failed!")
        sys.exit(1)
