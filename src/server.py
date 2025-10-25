#!/usr/bin/env python3
import os
import json
from datetime import datetime
from fastmcp import FastMCP
from pydexcom import Dexcom
from pydexcom.errors import AccountErrorEnum
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

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
        "capabilities": ["poke_connection_test", "greeting", "server_info", "echo", "dexcom_glucose_data", "comprehensive_food_analysis"],
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

@mcp.tool(description="Comprehensive food analysis with personality, macros, and helpful tips using Gemini AI")
def analyze_food(food_description: str) -> dict:
    """Get a comprehensive food analysis with personality, detailed macros, and helpful nutrition tips"""
    try:
        # Check if Gemini API key is configured
        if not os.getenv('GEMINI_API_KEY'):
            return {
                "error": "Gemini API key not configured",
                "message": "Please set GEMINI_API_KEY environment variable"
            }
        
        # Create Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create a comprehensive prompt that combines macros and personality
        prompt = f"""
        You are a warm, encouraging nutrition coach analyzing this food. Be friendly, helpful, and conversational!
        
        Food Description: "{food_description}"
        
        Provide a comprehensive analysis in this JSON format:
        {{
            "greeting": "<A friendly greeting about the food - like 'Oh, that sounds delicious!' or 'Nice choice!' or 'That looks like a satisfying meal!'>",
            "food_breakdown": "<Break down what's in this meal in a conversational way - like 'You've got a nice protein source with...' or 'I can see you're getting some good carbs from...'>",
            "nutritional_highlights": {{
                "calories": <estimated calories>,
                "carbohydrates_g": <grams of carbohydrates>,
                "protein_g": <grams of protein>,
                "fat_g": <grams of fat>,
                "fiber_g": <grams of fiber>,
                "sugar_g": <grams of sugar>,
                "sodium_mg": <milligrams of sodium>
            }},
            "whats_good": "<What's nutritionally good about this meal - like 'Great protein choice!' or 'Nice fiber content!' or 'Good balance of macros!'>",
            "whats_missing": "<What might be missing - like 'Could use some vegetables' or 'Maybe add some healthy fats' or 'Consider a side of fruit'>",
            "helpful_tips": "<Practical tips - like 'Try adding some greens' or 'Great choice for post-workout!' or 'Watch the sodium with that sauce'>",
            "encouragement": "<Encouraging message - like 'You're making good choices!' or 'This is a solid meal!' or 'Keep up the healthy eating!'>",
            "serving_size": "<estimated serving size>",
            "confidence": "<high/medium/low>",
            "analysis_notes": "<Technical notes about the analysis>"
        }}
        
        Guidelines:
        - Be warm, encouraging, and conversational
        - Provide accurate nutritional estimates
        - Consider portion sizes, cooking methods, and preparation
        - Give helpful, practical tips
        - Suggest what might be missing from the meal
        - Be positive but honest about nutritional value
        - Make the user feel good about their food choices while giving constructive advice
        
        Return ONLY the JSON object, no additional text.
        """
        
        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        try:
            # Clean up the response text (remove markdown code blocks if present)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            analysis_data = json.loads(response_text)
            
            return {
                "food_description": food_description,
                "analysis_method": "gemini_comprehensive_analysis",
                "analysis": analysis_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response with error info
            return {
                "food_description": food_description,
                "analysis_method": "gemini_comprehensive_analysis",
                "raw_response": response.text,
                "error": "Failed to parse Gemini response as JSON",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        return {
            "error": "Food analysis failed",
            "message": f"Failed to analyze food: {str(e)}",
            "food_description": food_description
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