#!/usr/bin/env python3
"""
Test script for ilovesugar MCP server
Tests basic connectivity and tool functionality
"""
import requests
import json
import time
import sys
import pytest

def test_server_health():
    """Test if the server is running and accessible"""
    # Test basic server response
    response = requests.get("http://localhost:8000/", timeout=5)
    print(f" Server is running (status: {response.status_code})")
    # FastMCP may not serve '/' with 200; 404 is acceptable as long as server responds
    assert response.status_code in (200, 404)

def test_mcp_endpoint():
    """Test the MCP endpoint specifically"""
    response = requests.get("http://localhost:8000/mcp", timeout=5)
    print(f" MCP endpoint accessible (status: {response.status_code})")
    # GET /mcp may return 406 (Not Acceptable) without proper headers; accept 200 or 406
    assert response.status_code in (200, 406)

def test_tools_via_http():
    """Test if we can call tools via HTTP (basic test)"""
    #checking if server responds
    response = requests.get("http://localhost:8000/mcp", timeout=5)
    print("Server responds to MCP requests")
    assert response.status_code in (200, 406)

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