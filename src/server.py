#!/usr/bin/env python3
import os
import json
from datetime import datetime
from fastmcp import FastMCP
from pydexcom import Dexcom
from pydexcom.errors import AccountErrorEnum
from dotenv import load_dotenv
import google.generativeai as genai
from diabetes_context import (
    track_meal_with_context,
    log_glucose_response,
    analyze_meal_patterns,
    get_smart_recommendations,
    learn_from_outcome,
    get_diabetes_summary
)

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
        "capabilities": ["poke_connection_test", "greeting", "server_info", "echo", "dexcom_glucose_data", "comprehensive_food_analysis", "insulin_dose_calculation", "diabetes_context_management"],
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

@mcp.tool(description="Calculate insulin dose based on carb count, current glucose, and insulin ratios")
def calculate_insulin_dose(
    carb_grams: float,
    insulin_to_carb_ratio: float = None,
    total_daily_dose: float = None,
    current_glucose: float = None,
    target_glucose: float = 120.0,
    correction_factor: float = None,
    use_dexcom_glucose: bool = True
) -> dict:
    """
    Calculate insulin dose based on carbohydrate intake and glucose levels.
    
    Args:
        carb_grams: Grams of carbohydrates in the meal
        insulin_to_carb_ratio: Units of insulin per gram of carbs (e.g., 10 means 1 unit per 10g carbs)
        total_daily_dose: Total daily insulin dose (used to calculate ratios if not provided)
        current_glucose: Current blood glucose in mg/dL (if not provided, will try to get from Dexcom)
        target_glucose: Target blood glucose in mg/dL (default: 120)
        correction_factor: mg/dL drop per unit of insulin (calculated from TDD if not provided)
        use_dexcom_glucose: Whether to automatically get current glucose from Dexcom
    """
    try:
        # Get current glucose from Dexcom if requested and not provided
        if use_dexcom_glucose and current_glucose is None:
            try:
                username = os.getenv('DEXCOM_USERNAME')
                password = os.getenv('DEXCOM_PASSWORD')
                region = os.getenv('DEXCOM_REGION', 'us')
                
                if username and password:
                    dexcom = Dexcom(username=username, password=password, region=region)
                    glucose_reading = dexcom.get_current_glucose_reading()
                    if glucose_reading:
                        current_glucose = glucose_reading.mg_dl
            except Exception as e:
                return {
                    "error": "Failed to get glucose from Dexcom",
                    "message": f"Could not retrieve current glucose: {str(e)}",
                    "suggestion": "Provide current_glucose parameter manually"
                }
        
        # Validate required parameters
        if carb_grams <= 0:
            return {
                "error": "Invalid carb count",
                "message": "Carbohydrate grams must be greater than 0"
            }
        
        if current_glucose is None:
            return {
                "error": "Current glucose required",
                "message": "Please provide current_glucose or ensure Dexcom integration is working"
            }
        
        # Calculate insulin-to-carb ratio if not provided
        if insulin_to_carb_ratio is None:
            if total_daily_dose is None or total_daily_dose <= 0:
                return {
                    "error": "Missing ratio information",
                    "message": "Please provide either insulin_to_carb_ratio or total_daily_dose"
                }
            # Use 500 rule: 500 / TDD = I:C ratio
            insulin_to_carb_ratio = 500 / total_daily_dose
        
        # Calculate correction factor if not provided
        if correction_factor is None:
            if total_daily_dose is None or total_daily_dose <= 0:
                return {
                    "error": "Missing correction factor",
                    "message": "Please provide either correction_factor or total_daily_dose"
                }
            # Use 1800 rule: 1800 / TDD = correction factor
            correction_factor = 1800 / total_daily_dose
        
        # Calculate mealtime insulin dose
        mealtime_dose = carb_grams / insulin_to_carb_ratio
        
        # Calculate correction dose
        glucose_difference = current_glucose - target_glucose
        correction_dose = 0.0
        
        if glucose_difference > 0:
            correction_dose = glucose_difference / correction_factor
        elif glucose_difference < 0:
            # If glucose is below target, we might want to reduce the mealtime dose
            # This is a safety consideration - consult healthcare provider
            correction_dose = glucose_difference / correction_factor
        
        # Calculate total insulin dose
        total_dose = mealtime_dose + correction_dose
        
        # Safety checks and warnings
        warnings = []
        safety_notes = []
        
        # Check for very high doses
        if total_dose > 20:
            warnings.append("High insulin dose calculated - please verify with healthcare provider")
        
        # Check for negative correction (glucose below target)
        if glucose_difference < -30:
            warnings.append("Current glucose is significantly below target - consider reducing insulin or eating first")
            safety_notes.append("Glucose below target may indicate need to eat before taking insulin")
        
        # Check for very high glucose
        if current_glucose > 300:
            warnings.append("Very high glucose reading - consider checking for ketones and consulting healthcare provider")
        
        # Check for very low glucose
        if current_glucose < 70:
            warnings.append("Low glucose reading - treat hypoglycemia before taking insulin")
            safety_notes.append("Do not take insulin if experiencing hypoglycemia")
        
        # Round to appropriate precision
        mealtime_dose_rounded = round(mealtime_dose, 1)
        correction_dose_rounded = round(correction_dose, 1)
        total_dose_rounded = round(total_dose, 1)
        
        return {
            "calculation_summary": {
                "carb_grams": carb_grams,
                "current_glucose": current_glucose,
                "target_glucose": target_glucose,
                "glucose_difference": round(glucose_difference, 1)
            },
            "ratios_used": {
                "insulin_to_carb_ratio": round(insulin_to_carb_ratio, 1),
                "correction_factor": round(correction_factor, 1)
            },
            "dose_breakdown": {
                "mealtime_dose": mealtime_dose_rounded,
                "correction_dose": correction_dose_rounded,
                "total_dose": total_dose_rounded
            },
            "recommendations": {
                "total_insulin_units": total_dose_rounded,
                "rounding_note": "Round to nearest 0.5 or 1 unit as advised by healthcare provider"
            },
            "safety_checks": {
                "warnings": warnings,
                "safety_notes": safety_notes,
                "disclaimer": "This calculation is for educational purposes. Always consult your healthcare provider before making insulin dosing decisions."
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": "Insulin calculation failed",
            "message": f"Failed to calculate insulin dose: {str(e)}"
        }

@mcp.tool(description="Track meal with context for Poke to remember patterns")
def track_meal_context(
    food_description: str,
    carb_grams: float,
    insulin_dose: float,
    pre_meal_glucose: float,
    notes: str = None
) -> dict:
    """Track a meal and store context for Poke to remember patterns"""
    return track_meal_with_context(
        food_description=food_description,
        carb_grams=carb_grams,
        insulin_dose=insulin_dose,
        pre_meal_glucose=pre_meal_glucose,
        notes=notes
    )

@mcp.tool(description="Log glucose response for Poke to track patterns")
def log_glucose_response_context(
    meal_description: str,
    pre_meal_glucose: float,
    post_meal_glucose: float,
    time_elapsed_minutes: int,
    insulin_dose_used: float
) -> dict:
    """Log glucose response for Poke to remember and analyze"""
    return log_glucose_response(
        meal_description=meal_description,
        pre_meal_glucose=pre_meal_glucose,
        post_meal_glucose=post_meal_glucose,
        time_elapsed_minutes=time_elapsed_minutes,
        insulin_dose_used=insulin_dose_used
    )

@mcp.tool(description="Ask Poke to analyze meal patterns from memory")
def analyze_meal_patterns_context(
    food_type: str = None,
    time_period: str = "last_week"
) -> dict:
    """Generate context for Poke to analyze meal patterns"""
    return analyze_meal_patterns(
        food_type=food_type,
        time_period=time_period
    )

@mcp.tool(description="Get personalized recommendations based on Poke's memory")
def get_smart_recommendations_context(
    current_situation: str
) -> dict:
    """Generate context for Poke to give personalized recommendations"""
    return get_smart_recommendations(current_situation=current_situation)

@mcp.tool(description="Learn from meal outcomes for better future predictions")
def learn_from_outcome_context(
    meal_description: str,
    predicted_glucose_rise: float,
    actual_glucose_rise: float,
    insulin_ratio_used: float
) -> dict:
    """Help Poke learn from actual outcomes vs predictions"""
    return learn_from_outcome(
        meal_description=meal_description,
        predicted_glucose_rise=predicted_glucose_rise,
        actual_glucose_rise=actual_glucose_rise,
        insulin_ratio_used=insulin_ratio_used
    )

@mcp.tool(description="Get diabetes management summary and available tools")
def get_diabetes_management_summary() -> dict:
    """Get a summary of diabetes management context for Poke"""
    return get_diabetes_summary()

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