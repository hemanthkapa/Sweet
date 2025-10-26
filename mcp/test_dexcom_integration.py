#!/usr/bin/env python3
"""
Test script for Dexcom integration
This script tests the Dexcom tools via share
"""

import os
import sys
from dotenv import load_dotenv

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
        print(" Dexcom credentials not configured")
        print("Please set DEXCOM_USERNAME and DEXCOM_PASSWORD environment variables")
        print("\nExample .env file:")
        print("DEXCOM_USERNAME=your_username_or_email_or_phone")
        print("DEXCOM_PASSWORD=your_password")
        print("DEXCOM_REGION=us  # Options: us, ous, jp")
        return False
    
    print(f" Credentials found: {username} (region: {region})")
    
    try:
        # Test pydexcom directly
        from pydexcom import Dexcom
        from pydexcom.errors import AccountErrorEnum
        
        print("\nTesting Dexcom connection...")
        dexcom = Dexcom(username=username, password=password, region=region)
        
        print("Testing get_current_glucose_reading()...")
        glucose_reading = dexcom.get_current_glucose_reading()
        
        if glucose_reading:
            print(f" Current glucose: {glucose_reading.value} mg/dL ({glucose_reading.mmol_l} mmol/L)")
            print(f"   Trend: {glucose_reading.trend_direction} {glucose_reading.trend_arrow}")
            print(f"   Time: {glucose_reading.datetime}")
        else:
            print("No current glucose reading available")
        
        print("\nTesting get_latest_glucose_reading()...")
        glucose_reading = dexcom.get_latest_glucose_reading()
        
        if glucose_reading:
            print(f" Latest glucose: {glucose_reading.value} mg/dL ({glucose_reading.mmol_l} mmol/L)")
            print(f"   Trend: {glucose_reading.trend_direction} {glucose_reading.trend_arrow}")
            print(f"   Time: {glucose_reading.datetime}")
        else:
            print("No latest glucose reading available")
        
        print("\nTesting get_glucose_readings(minutes=60)...")
        glucose_readings = dexcom.get_glucose_readings(minutes=60)
        
        if glucose_readings:
            print(f"Found {len(glucose_readings)} readings in the last 60 minutes")
            if len(glucose_readings) > 0:
                latest = glucose_readings[0]
                print(f"   Latest: {latest.value} mg/dL at {latest.datetime}")
        else:
            print("No glucose readings available for the last 60 minutes")
        
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure pydexcom is installed: pip install pydexcom")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_dexcom_tools()
    if success:
        print("\n Dexcom integration test completed!")
    else:
        print("\nDexcom integration test failed!")
        sys.exit(1)
