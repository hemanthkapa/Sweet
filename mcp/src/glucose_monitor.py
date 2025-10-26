#!/usr/bin/env python3
"""
Background glucose monitoring utility.

Checks Dexcom glucose every `interval_minutes` and triggers an alert when
value is outside the [low_threshold, high_threshold] range.

"""

from __future__ import annotations

import os
import json
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any

from pydexcom import Dexcom
import google.generativeai as genai
import os

# Internal singleton state
_monitor_thread: Optional[threading.Thread] = None
_stop_event: Optional[threading.Event] = None
_status: Dict[str, Any] = {
    "running": False,
    "last_check": None,
    "last_value": None,
    "last_alert": None,
    "low_threshold": 70,
    "high_threshold": 250,
    "interval_minutes": 10,
    "webhook_url": None,
    "last_error": None,
}


def _get_ai_suggestion(glucose_value: float, alert_level: str, threshold: float) -> str:
    """Get AI-powered suggestion based on glucose context using Gemini."""
    try:
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create context-aware prompt
        prompt = f"""
        You are a diabetes management expert providing immediate, actionable advice for a glucose alert. You provide general advice too about being active, drinking enough water, maintiaing good sleep. 
        
        Current Situation:
        - Glucose Level: {glucose_value} mg/dL
        - Alert Type: {alert_level.upper()}
        - Threshold: {threshold} mg/dL
        - Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        Provide a concise, immediate action suggestion (1-2 sentences) that includes:
        1. What to do RIGHT NOW
        2. When to recheck glucose
        3. Any warning signs to watch for
        
        Be specific, actionable, and urgent. Focus on immediate safety and next steps.
        
        Format: "IMMEDIATE ACTION: [specific action]. [When to recheck]. [Warning signs to watch]."
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        # Simple fallback without hardcoded medical advice
        return f"AI suggestion unavailable. Please consult your healthcare provider for guidance on glucose level {glucose_value} mg/dL."

def _log_alert(message: str, payload: Dict[str, Any]) -> None:
    """Log alert to file and console."""
    try:
        # Write to local log file for audit/debug
        line = f"{datetime.now().isoformat()} | {message} | {json.dumps(payload, ensure_ascii=False)}\n"
        try:
            with open(os.path.join(os.getcwd(), "alerts.log"), "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass
        print(f"[GlucoseMonitor] {line}", end="")
    except Exception as e:
        print(f"[GlucoseMonitor] Failed to log alert: {e}")


def _get_current_glucose_value() -> Optional[float]:
    """Return current glucose in mg/dL using Dexcom Share via pydexcom, or None on error."""
    try:
        username = os.getenv('DEXCOM_USERNAME')
        password = os.getenv('DEXCOM_PASSWORD')
        region = os.getenv('DEXCOM_REGION', 'us')
        if not username or not password:
            _status["last_error"] = "Dexcom credentials not configured"
            return None
        dexcom = Dexcom(username=username, password=password, region=region)
        reading = dexcom.get_current_glucose_reading()
        if reading:
            return float(reading.mg_dl)
        _status["last_error"] = "No current glucose reading available"
        return None
    except Exception as e:
        _status["last_error"] = f"Dexcom error: {e}"
        return None


def _monitor_loop(low_threshold: float, high_threshold: float, interval_minutes: int):
    interval_seconds = max(60, int(interval_minutes * 60))  # safety lower bound 60s
    _status.update({
        "running": True,
        "low_threshold": low_threshold,
        "high_threshold": high_threshold,
        "interval_minutes": interval_minutes,
        "webhook_url": None,
        "last_error": None,
    })

    while _stop_event and not _stop_event.is_set():
        now = datetime.now().isoformat()
        value = _get_current_glucose_value()
        _status["last_check"] = now
        _status["last_value"] = value

        if value is not None:
            if value < low_threshold:
                # Get AI-powered suggestion for low glucose
                suggestion = _get_ai_suggestion(value, "low", low_threshold)
                msg = f"🚨 GLUCOSE ALERT: LOW at {value} mg/dL (below {low_threshold})"
                payload = {
                    "level": "low",
                    "value": value,
                    "threshold": low_threshold,
                    "timestamp": now,
                    "suggestion": suggestion,
                    "ai_generated": True
                }
                _status["last_alert"] = payload
                _log_alert(msg, payload)
            elif value > high_threshold:
                # Get AI-powered suggestion for high glucose
                suggestion = _get_ai_suggestion(value, "high", high_threshold)
                msg = f"🚨 GLUCOSE ALERT: HIGH at {value} mg/dL (above {high_threshold})"
                payload = {
                    "level": "high",
                    "value": value,
                    "threshold": high_threshold,
                    "timestamp": now,
                    "suggestion": suggestion,
                    "ai_generated": True
                }
                _status["last_alert"] = payload
                _log_alert(msg, payload)

        # Sleep until next check, but wake early if stopped
        for _ in range(interval_seconds):
            if _stop_event and _stop_event.is_set():
                break
            time.sleep(1)

    _status["running"] = False


def start_monitoring(
    low_threshold: float = 70,
    high_threshold: float = 250,
    interval_minutes: int = 10,
) -> Dict[str, Any]:
    """Start the background glucose monitor. Returns current status."""
    global _monitor_thread, _stop_event
    if _status.get("running"):
        return {
            "started": False,
            "status": _status,
            "message": "Glucose monitor already running"
        }

    _stop_event = threading.Event()
    _monitor_thread = threading.Thread(
        target=_monitor_loop,
        args=(low_threshold, high_threshold, interval_minutes),
        daemon=True,
    )
    _monitor_thread.start()
    # Give the thread a moment to initialize status
    time.sleep(0.1)
    return {
        "started": True,
        "status": _status,
        "message": "Glucose monitor started with immediate suggestions"
    }


def stop_monitoring() -> Dict[str, Any]:
    """Stop the background glucose monitor. Returns final status."""
    global _monitor_thread, _stop_event
    if not _status.get("running"):
        return {
            "stopped": False,
            "status": _status,
            "message": "Glucose monitor is not running"
        }

    if _stop_event:
        _stop_event.set()
    if _monitor_thread and _monitor_thread.is_alive():
        _monitor_thread.join(timeout=5)
    _monitor_thread = None
    _stop_event = None
    return {
        "stopped": True,
        "status": _status,
        "message": "Glucose monitor stopped"
    }


def status() -> Dict[str, Any]:
    """Return current monitor status snapshot."""
    return dict(_status)
