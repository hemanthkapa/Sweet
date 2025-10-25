#!/usr/bin/env python3
import os
import json
from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP("ilovesugar MCP Server")

@mcp.tool(description="Test connection to Poke - returns server status and timestamp")
def test_poke_connection() -> dict:
    """Test if Poke can successfully connect to this MCP server"""
    return {
        "status": "connected",
        "server": "ilovesugar MCP Server",
        "timestamp": datetime.now().isoformat(),
        "message": "Poke connection successful!"
    }

@mcp.tool(description="Greet a user by name with a welcome message from the MCP server")
def greet(name: str) -> str:
    return f"Hello, {name}! Welcome to ilovesugar MCP server!"

@mcp.tool(description="Get detailed server information including environment and capabilities")
def get_server_info() -> dict:
    return {
        "server_name": "ilovesugar MCP Server",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": os.sys.version.split()[0],
        "capabilities": ["poke_connection_test", "greeting", "server_info", "echo"],
        "status": "ready"
    }

@mcp.tool(description="Simple echo tool to test basic functionality")
def echo(message: str) -> str:
    """Echo back the message to test basic tool functionality"""
    return f"Echo: {message}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting FastMCP server on {host}:{port}")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )