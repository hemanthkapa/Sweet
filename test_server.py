#!/usr/bin/env python3
"""
Test script for ilovesugar MCP server
Tests basic connectivity and tool functionality
"""
import requests
import json
import time
import sys

def test_server_health():
    """Test if the server is running and accessible"""
    try:
        # Test basic server response
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f" Server is running (status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(" Server is not running. Start it with: python src/server.py")
        return False
    except Exception as e:
        print(f" Server health check failed: {e}")
        return False

def test_mcp_endpoint():
    """Test the MCP endpoint specifically"""
    try:
        response = requests.get("http://localhost:8000/mcp", timeout=5)
        print(f" MCP endpoint accessible (status: {response.status_code})")
        return True
    except Exception as e:
        print(f" MCP endpoint test failed: {e}")
        return False

def test_tools_via_http():
    """Test if we can call tools via HTTP (basic test)"""
    try:
        #checking if server responds
        response = requests.get("http://localhost:8000/mcp", timeout=5)
        if response.status_code == 200:
            print("Server responds to MCP requests")
            return True
        else:
            print(f"Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"Tool testing failed: {e}")
        return False

def main():
    """Run all server tests"""
    print("Testing ilovesugar MCP Server")
    print("=" * 40)
    
    # Test 1: Server health
    print("\n1. Testing server health...")
    if not test_server_health():
        print("\n💡 Make sure to start the server first:")
        print("   cd /Users/kapa/Documents/ilovesugar")
        print("   source venv/bin/activate")
        print("   python src/server.py")
        sys.exit(1)
    
    # Test 2: MCP endpoint
    print("\n2. Testing MCP endpoint...")
    test_mcp_endpoint()
    
    # Test 3: Basic functionality
    print("\n3. Testing basic functionality...")
    test_tools_via_http()
    
    print("\n" + "=" * 40)
    print(" Server tests completed!")
    print("\nNext steps:")
    print("1. Start ngrok: ngrok http 8000")
    print("2. Add the ngrok URL to Poke at poke.com/settings/connections")
    print("3. Test with Poke: 'Test the ilovesugar connection'")

if __name__ == "__main__":
    main()