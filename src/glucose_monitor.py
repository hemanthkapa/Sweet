#!/usr/bin/env python3
"""
Background glucose monitoring utility.

Checks Dexcom glucose every `interval_minutes` and triggers an alert when
value is outside the [low_threshold, high_threshold] range.

Alerts are sent to an optional webhook URL provided via:
- function parameter `webhook_url`, or
- environment variable `POKE_WEBHOOK_URL` (fallback)

If no webhook is configured, the alert is printed to stdout and appended to
`alerts.log` in the project root.
"""

from __future__ import annotations

import os
import json
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any

import requests
from pydexcom import Dexcom

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


def _post_webhook(message: str, payload: Dict[str, Any], webhook_url: Optional[str]) -> None:
    """Send alert to webhook if configured, else log/print."""
    try:
        if webhook_url:
            headers = {"Content-Type": "application/json"}
            requests.post(webhook_url, data=json.dumps({
                "type": "glucose_alert",
                "message": message,
                **payload
            }), headers=headers, timeout=10)
        # Always also write a local log line for audit/debug
        line = f"{datetime.now().isoformat()} | {message} | {json.dumps(payload, ensure_ascii=False)}\n"
        try:
            with open(os.path.join(os.getcwd(), "alerts.log"), "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass
        print(f"[GlucoseMonitor] {line}", end="")
    except Exception as e:
        print(f"[GlucoseMonitor] Failed to send webhook: {e}")


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


def _monitor_loop(low_threshold: float, high_threshold: float, interval_minutes: int, webhook_url: Optional[str]):
    interval_seconds = max(60, int(interval_minutes * 60))  # safety lower bound 60s
    _status.update({
        "running": True,
        "low_threshold": low_threshold,
        "high_threshold": high_threshold,
        "interval_minutes": interval_minutes,
        "webhook_url": webhook_url,
        "last_error": None,
    })

    while _stop_event and not _stop_event.is_set():
        now = datetime.now().isoformat()
        value = _get_current_glucose_value()
        _status["last_check"] = now
        _status["last_value"] = value

        if value is not None:
            if value < low_threshold:
                msg = f"Danger: glucose LOW at {value} mg/dL (threshold {low_threshold})."
                payload = {
                    "level": "low",
                    "value": value,
                    "threshold": low_threshold,
                    "timestamp": now,
                }
                _status["last_alert"] = payload
                _post_webhook(msg, payload, webhook_url)
            elif value > high_threshold:
                msg = f"Danger: glucose HIGH at {value} mg/dL (threshold {high_threshold})."
                payload = {
                    "level": "high",
                    "value": value,
                    "threshold": high_threshold,
                    "timestamp": now,
                }
                _status["last_alert"] = payload
                _post_webhook(msg, payload, webhook_url)

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
    webhook_url: Optional[str] = None,
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
    webhook = webhook_url or os.getenv("POKE_WEBHOOK_URL") or os.getenv("ALERT_WEBHOOK_URL")
    _monitor_thread = threading.Thread(
        target=_monitor_loop,
        args=(low_threshold, high_threshold, interval_minutes, webhook),
        daemon=True,
    )
    _monitor_thread.start()
    # Give the thread a moment to initialize status
    time.sleep(0.1)
    return {
        "started": True,
        "status": _status,
        "message": "Glucose monitor started"
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
