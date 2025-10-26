#!/usr/bin/env python3
"""
Diabetes Context Management Module
Provides context-aware tools for Poke to track and learn from diabetes patterns
"""

from datetime import datetime
from typing import Optional, Dict, Any

class DiabetesContextManager:
    """Manages diabetes-related context for Poke's memory system"""
    
    def __init__(self):
        self.context_templates = {
            "meal_log": self._create_meal_log_context,
            "glucose_response": self._create_glucose_response_context,
            "pattern_analysis": self._create_pattern_analysis_context,
            "smart_recommendations": self._create_smart_recommendations_context,
            "outcome_learning": self._create_outcome_learning_context
        }
    
    def _create_meal_log_context(self, **kwargs) -> str:
        """Create context for meal logging"""
        return f"""
MEAL LOGGED: {kwargs.get('food_description', 'Unknown food')}
- Carbs: {kwargs.get('carb_grams', 'Unknown')}g
- Insulin: {kwargs.get('insulin_dose', 'Unknown')} units
- Pre-meal glucose: {kwargs.get('pre_meal_glucose', 'Unknown')} mg/dL
- Time: {kwargs.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}
- Notes: {kwargs.get('notes', 'None')}

Please remember this meal and its details for future pattern analysis.
"""
    
    def _create_glucose_response_context(self, **kwargs) -> str:
        """Create context for glucose response tracking"""
        glucose_rise = kwargs.get('post_meal_glucose', 0) - kwargs.get('pre_meal_glucose', 0)
        return f"""
GLUCOSE RESPONSE LOGGED:
- Meal: {kwargs.get('meal_description', 'Unknown')}
- Pre-meal: {kwargs.get('pre_meal_glucose', 'Unknown')} mg/dL
- Post-meal: {kwargs.get('post_meal_glucose', 'Unknown')} mg/dL
- Rise: {glucose_rise} mg/dL
- Time elapsed: {kwargs.get('time_elapsed_minutes', 'Unknown')} minutes
- Insulin used: {kwargs.get('insulin_dose_used', 'Unknown')} units

Please remember this response pattern for future analysis.
"""
    
    def _create_pattern_analysis_context(self, **kwargs) -> str:
        """Create context for pattern analysis requests"""
        return f"""
Please analyze my meal patterns for {kwargs.get('food_type', 'all foods')} over the {kwargs.get('time_period', 'last_week')}.

Look for:
1. Which foods cause the biggest glucose spikes
2. Best insulin ratios for different foods
3. Time-of-day effects on glucose response
4. Any patterns in my eating habits

Use your memory of my previous meals to provide insights.
"""
    
    def _create_smart_recommendations_context(self, **kwargs) -> str:
        """Create context for smart recommendations"""
        return f"""
Current situation: {kwargs.get('current_situation', 'General diabetes management')}

Based on your memory of my previous meals, glucose readings, and insulin doses:
1. What would you recommend for my next meal?
2. What insulin ratio should I use?
3. Any patterns you've noticed that I should be aware of?
4. Any foods that consistently cause problems?

Please provide personalized advice based on my historical data.
"""
    
    def _create_outcome_learning_context(self, **kwargs) -> str:
        """Create context for learning from outcomes"""
        accuracy = abs(kwargs.get('predicted_glucose_rise', 0) - kwargs.get('actual_glucose_rise', 0))
        return f"""
OUTCOME LEARNING:
- Meal: {kwargs.get('meal_description', 'Unknown')}
- Predicted rise: {kwargs.get('predicted_glucose_rise', 'Unknown')} mg/dL
- Actual rise: {kwargs.get('actual_glucose_rise', 'Unknown')} mg/dL
- Accuracy: {accuracy} mg/dL difference
- Insulin ratio used: {kwargs.get('insulin_ratio_used', 'Unknown')}

Please update your understanding of my glucose responses based on this outcome.
"""

def track_meal_with_context(
    food_description: str,
    carb_grams: float,
    insulin_dose: float,
    pre_meal_glucose: float,
    notes: str = None
) -> Dict[str, Any]:
    """
    Track a meal and store context for Poke to remember patterns
    
    Args:
        food_description: Description of the food eaten
        carb_grams: Grams of carbohydrates in the meal
        insulin_dose: Insulin units taken
        pre_meal_glucose: Blood glucose before meal (mg/dL)
        notes: Additional notes about the meal
    
    Returns:
        Dictionary with tracking info and context for Poke
    """
    context_manager = DiabetesContextManager()
    timestamp = datetime.now().isoformat()
    
    context = context_manager._create_meal_log_context(
        food_description=food_description,
        carb_grams=carb_grams,
        insulin_dose=insulin_dose,
        pre_meal_glucose=pre_meal_glucose,
        notes=notes,
        timestamp=timestamp
    )
    
    return {
        "meal_logged": True,
        "context_for_poke": context,
        "meal_summary": {
            "food": food_description,
            "carbs": carb_grams,
            "insulin": insulin_dose,
            "pre_glucose": pre_meal_glucose,
            "timestamp": timestamp
        },
        "instructions": "Please remember this meal and its details for future pattern analysis."
    }

def log_glucose_response(
    meal_description: str,
    pre_meal_glucose: float,
    post_meal_glucose: float,
    time_elapsed_minutes: int,
    insulin_dose_used: float
) -> Dict[str, Any]:
    """
    Log glucose response for Poke to remember and analyze
    
    Args:
        meal_description: Description of the meal
        pre_meal_glucose: Glucose before meal (mg/dL)
        post_meal_glucose: Glucose after meal (mg/dL)
        time_elapsed_minutes: Time between measurements
        insulin_dose_used: Insulin units that were taken
    
    Returns:
        Dictionary with response data and context for Poke
    """
    context_manager = DiabetesContextManager()
    glucose_rise = post_meal_glucose - pre_meal_glucose
    timestamp = datetime.now().isoformat()
    
    context = context_manager._create_glucose_response_context(
        meal_description=meal_description,
        pre_meal_glucose=pre_meal_glucose,
        post_meal_glucose=post_meal_glucose,
        time_elapsed_minutes=time_elapsed_minutes,
        insulin_dose_used=insulin_dose_used
    )
    
    return {
        "response_logged": True,
        "context_for_poke": context,
        "glucose_response": {
            "meal": meal_description,
            "pre_meal_glucose": pre_meal_glucose,
            "post_meal_glucose": post_meal_glucose,
            "glucose_rise": glucose_rise,
            "time_elapsed": time_elapsed_minutes,
            "insulin_used": insulin_dose_used,
            "timestamp": timestamp
        },
        "instructions": "Please remember this response pattern for future analysis."
    }

def analyze_meal_patterns(
    food_type: str = None,
    time_period: str = "last_week"
) -> Dict[str, Any]:
    """
    Generate context for Poke to analyze meal patterns
    
    Args:
        food_type: Specific type of food to analyze (optional)
        time_period: Time period to analyze (e.g., "last_week", "last_month")
    
    Returns:
        Dictionary with analysis request for Poke
    """
    context_manager = DiabetesContextManager()
    
    context = context_manager._create_pattern_analysis_context(
        food_type=food_type or "all foods",
        time_period=time_period
    )
    
    return {
        "analysis_request": context,
        "context_type": "pattern_analysis",
        "parameters": {
            "food_type": food_type,
            "time_period": time_period
        },
        "instructions": "Please analyze my meal patterns and provide insights based on your memory."
    }

def get_smart_recommendations(
    current_situation: str
) -> Dict[str, Any]:
    """
    Generate context for Poke to give personalized recommendations
    
    Args:
        current_situation: Description of current situation
    
    Returns:
        Dictionary with recommendation request for Poke
    """
    context_manager = DiabetesContextManager()
    
    context = context_manager._create_smart_recommendations_context(
        current_situation=current_situation
    )
    
    return {
        "recommendation_request": context,
        "context_type": "smart_recommendations",
        "current_situation": current_situation,
        "instructions": "Please provide personalized advice based on my historical data."
    }

def learn_from_outcome(
    meal_description: str,
    predicted_glucose_rise: float,
    actual_glucose_rise: float,
    insulin_ratio_used: float
) -> Dict[str, Any]:
    """
    Help Poke learn from actual outcomes vs predictions
    
    Args:
        meal_description: Description of the meal
        predicted_glucose_rise: Predicted glucose rise (mg/dL)
        actual_glucose_rise: Actual glucose rise (mg/dL)
        insulin_ratio_used: Insulin ratio that was used
    
    Returns:
        Dictionary with learning data and context for Poke
    """
    context_manager = DiabetesContextManager()
    accuracy = abs(predicted_glucose_rise - actual_glucose_rise)
    timestamp = datetime.now().isoformat()
    
    context = context_manager._create_outcome_learning_context(
        meal_description=meal_description,
        predicted_glucose_rise=predicted_glucose_rise,
        actual_glucose_rise=actual_glucose_rise,
        insulin_ratio_used=insulin_ratio_used
    )
    
    return {
        "learning_logged": True,
        "context_for_poke": context,
        "outcome_analysis": {
            "meal": meal_description,
            "predicted_rise": predicted_glucose_rise,
            "actual_rise": actual_glucose_rise,
            "accuracy": accuracy,
            "insulin_ratio": insulin_ratio_used,
            "timestamp": timestamp
        },
        "instructions": "Please update your understanding of my glucose responses based on this outcome."
    }

def get_diabetes_summary() -> Dict[str, Any]:
    """
    Get a summary of diabetes management context for Poke
    
    Returns:
        Dictionary with summary information
    """
    return {
        "diabetes_management_summary": {
            "available_tools": [
                "track_meal_with_context",
                "log_glucose_response", 
                "analyze_meal_patterns",
                "get_smart_recommendations",
                "learn_from_outcome"
            ],
            "purpose": "Help Poke track and learn from diabetes patterns",
            "context_types": [
                "meal_logging",
                "glucose_response_tracking",
                "pattern_analysis",
                "smart_recommendations",
                "outcome_learning"
            ]
        },
        "instructions": "Use these tools to help manage diabetes by tracking patterns and learning from outcomes."
    }
