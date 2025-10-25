#!/usr/bin/env python3
import os
import json
from datetime import datetime
from fastmcp import FastMCP
from pydexcom import Dexcom
from pydexcom.errors import AccountErrorEnum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
        "capabilities": ["poke_connection_test", "greeting", "server_info", "echo", "dexcom_glucose_data"],
        "status": "ready"
    }

@mcp.tool(description="Simple echo tool to test basic functionality")
def echo(message: str) -> str:
    """Echo back the message to test basic tool functionality"""
    return f"Echo: {message}"

@mcp.tool(description="Get current glucose reading from Dexcom CGM")
def get_current_glucose() -> dict:
    """Get the most recent glucose reading from Dexcom Share service"""
    try:
        
        username = os.getenv('DEXCOM_USERNAME')
        password = os.getenv('DEXCOM_PASSWORD')
        region = os.getenv('DEXCOM_REGION', 'us')  # Default to US region
        
        if not username or not password:
            return {
                "error": "Dexcom credentials not configured",
                "message": "Please set DEXCOM_USERNAME and DEXCOM_PASSWORD environment variables"
            }
        
        # Initialize Dexcom client
        dexcom = Dexcom(username=username, password=password, region=region)
        
        # Get current glucose reading
        glucose_reading = dexcom.get_current_glucose_reading()
        
        if glucose_reading:
            return {
                "value": glucose_reading.value,
                "mg_dl": glucose_reading.mg_dl,
                "mmol_l": glucose_reading.mmol_l,
                "trend": glucose_reading.trend,
                "trend_direction": glucose_reading.trend_direction,
                "trend_description": glucose_reading.trend_description,
                "trend_arrow": glucose_reading.trend_arrow,
                "datetime": glucose_reading.datetime.isoformat(),
                "raw_data": glucose_reading.json
            }
        else:
            return {
                "error": "No glucose reading available",
                "message": "No current glucose reading found"
            }
            
    except AccountErrorEnum as e:
        return {
            "error": "Dexcom authentication failed",
            "message": f"Invalid credentials or account error: {str(e)}"
        }
    except Exception as e:
        return {
            "error": "Dexcom API error",
            "message": f"Failed to retrieve glucose data: {str(e)}"
        }

@mcp.tool(description="Get latest glucose reading from Dexcom CGM")
def get_latest_glucose() -> dict:
    """Get the latest glucose reading from Dexcom Share service"""
    try:
        
        username = os.getenv('DEXCOM_USERNAME')
        password = os.getenv('DEXCOM_PASSWORD')
        region = os.getenv('DEXCOM_REGION', 'us')  # Default to US region
        
        if not username or not password:
            return {
                "error": "Dexcom credentials not configured",
                "message": "Please set DEXCOM_USERNAME and DEXCOM_PASSWORD environment variables"
            }
        
        # Initialize Dexcom client
        dexcom = Dexcom(username=username, password=password, region=region)
        
        # Get latest glucose reading
        glucose_reading = dexcom.get_latest_glucose_reading()
        
        if glucose_reading:
            return {
                "value": glucose_reading.value,
                "mg_dl": glucose_reading.mg_dl,
                "mmol_l": glucose_reading.mmol_l,
                "trend": glucose_reading.trend,
                "trend_direction": glucose_reading.trend_direction,
                "trend_description": glucose_reading.trend_description,
                "trend_arrow": glucose_reading.trend_arrow,
                "datetime": glucose_reading.datetime.isoformat(),
                "raw_data": glucose_reading.json
            }
        else:
            return {
                "error": "No glucose reading available",
                "message": "No latest glucose reading found"
            }
            
    except AccountErrorEnum as e:
        return {
            "error": "Dexcom authentication failed",
            "message": f"Invalid credentials or account error: {str(e)}"
        }
    except Exception as e:
        return {
            "error": "Dexcom API error",
            "message": f"Failed to retrieve glucose data: {str(e)}"
        }

@mcp.tool(description="Get glucose readings from Dexcom CGM for a specific time range")
def get_glucose_readings(minutes: int = 60) -> dict:
    """Get glucose readings from Dexcom Share service for the specified number of minutes"""
    try:
        
        username = os.getenv('DEXCOM_USERNAME')
        password = os.getenv('DEXCOM_PASSWORD')
        region = os.getenv('DEXCOM_REGION', 'us')  # Default to US region
        
        if not username or not password:
            return {
                "error": "Dexcom credentials not configured",
                "message": "Please set DEXCOM_USERNAME and DEXCOM_PASSWORD environment variables"
            }
        
        # Initialize Dexcom client
        dexcom = Dexcom(username=username, password=password, region=region)
        
        # Get glucose readings for the specified time range
        glucose_readings = dexcom.get_glucose_readings(minutes=minutes)
        
        if glucose_readings:
            readings_data = []
            for reading in glucose_readings:
                readings_data.append({
                    "value": reading.value,
                    "mg_dl": reading.mg_dl,
                    "mmol_l": reading.mmol_l,
                    "trend": reading.trend,
                    "trend_direction": reading.trend_direction,
                    "trend_description": reading.trend_description,
                    "trend_arrow": reading.trend_arrow,
                    "datetime": reading.datetime.isoformat(),
                    "raw_data": reading.json
                })
            
            return {
                "readings": readings_data,
                "count": len(readings_data),
                "time_range_minutes": minutes
            }
        else:
            return {
                "error": "No glucose readings available",
                "message": f"No glucose readings found for the last {minutes} minutes"
            }
            
    except AccountErrorEnum as e:
        return {
            "error": "Dexcom authentication failed",
            "message": f"Invalid credentials or account error: {str(e)}"
        }
    except Exception as e:
        return {
            "error": "Dexcom API error",
            "message": f"Failed to retrieve glucose data: {str(e)}"
        }

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