#!/usr/bin/env python3
"""
Notifications module for sending glucose alerts via SMS (Twilio) and managing recipients.

- Reads Twilio credentials from environment variables:
  TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM
- Reads recipients from either a JSON file or environment variable ALERT_RECIPIENTS.
  - ALERT_RECIPIENTS: comma-separated phone numbers, e.g. "+15551234567,+15557654321"
  - ALERT_RECIPIENTS_FILE: optional path to a JSON file storing an array of {name, phone}

Safe defaults:
- If Twilio isn't configured or import fails, we fall back to dry-run logging (no external calls).
- All sends are best-effort and never crash the caller; errors are returned in the result list.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional


DEFAULT_RECIPIENTS_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'recipients.json')
)


def _recipients_file_path() -> str:
    return os.getenv('ALERT_RECIPIENTS_FILE', DEFAULT_RECIPIENTS_FILE)


def _load_file_recipients() -> List[Dict[str, str]]:
    path = _recipients_file_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                # Normalize entries
                norm = []
                for item in data:
                    if isinstance(item, dict) and 'phone' in item:
                        norm.append({
                            'name': item.get('name') or '',
                            'phone': str(item['phone']).strip()
                        })
                return norm
    except Exception:
        pass
    return []


def _save_file_recipients(items: List[Dict[str, str]]) -> None:
    path = _recipients_file_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
    except Exception:
        # Best-effort; upstream should surface an error if needed
        pass


def list_recipients() -> List[Dict[str, str]]:
    """Return the merged list of alert recipients from file and env.

    Environment variable ALERT_RECIPIENTS (comma-separated phone numbers)
    is merged with the file-based list (deduped by phone).
    """
    file_list = _load_file_recipients()
    by_phone = {r['phone']: r for r in file_list if 'phone' in r and r['phone']}

    env_list: List[Dict[str, str]] = []
    env_str = os.getenv('ALERT_RECIPIENTS', '').strip()
    if env_str:
        for phone in [p.strip() for p in env_str.split(',') if p.strip()]:
            if phone not in by_phone:
                env_list.append({'name': '', 'phone': phone})

    # Merge and sort by name/phone for deterministic order
    merged = list(by_phone.values()) + env_list
    merged.sort(key=lambda x: (x.get('name') or '', x.get('phone') or ''))
    return merged


def add_recipient(name: str, phone: str) -> Dict[str, Any]:
    """Add a recipient to the file-backed list (env recipients are read-only)."""
    phone = (phone or '').strip()
    if not phone:
        return {"added": False, "error": "Phone is required"}

    items = _load_file_recipients()
    if any(r.get('phone') == phone for r in items):
        return {"added": False, "message": "Recipient already exists", "recipients": items}

    items.append({"name": name or '', "phone": phone})
    _save_file_recipients(items)
    return {"added": True, "recipients": items}


def remove_recipient(phone: str) -> Dict[str, Any]:
    """Remove a recipient by phone from the file-backed list."""
    phone = (phone or '').strip()
    items = _load_file_recipients()
    new_items = [r for r in items if r.get('phone') != phone]
    if len(new_items) == len(items):
        return {"removed": False, "message": "Recipient not found", "recipients": items}
    _save_file_recipients(new_items)
    return {"removed": True, "recipients": new_items}


@dataclass
class TwilioConfig:
    account_sid: Optional[str]
    auth_token: Optional[str]
    from_number: Optional[str]
    dry_run: bool


def _get_twilio_config() -> TwilioConfig:
    sid = os.getenv('TWILIO_ACCOUNT_SID')
    token = os.getenv('TWILIO_AUTH_TOKEN')
    from_num = os.getenv('TWILIO_FROM')
    dry_run_env = os.getenv('TWILIO_DRY_RUN', '').lower() in ('1', 'true', 'yes')

    # If any critical fields missing, force dry-run
    dry_run = dry_run_env or not (sid and token and from_num)
    return TwilioConfig(account_sid=sid, auth_token=token, from_number=from_num, dry_run=dry_run)


def _twilio_client_or_none(cfg: TwilioConfig):
    if cfg.dry_run:
        return None
    try:
        from twilio.rest import Client  # lazy import
        return Client(cfg.account_sid, cfg.auth_token)
    except Exception:
        return None


def send_sms_to_all(message: str) -> Dict[str, Any]:
    """Send an SMS to all recipients. Returns a summary result.

    This function is resilient: if Twilio is not configured or import fails,
    it will log a dry-run action and return without raising.
    """
    recipients = list_recipients()
    cfg = _get_twilio_config()
    client = _twilio_client_or_none(cfg)

    results = []
    for r in recipients:
        phone = r.get('phone')
        name = r.get('name') or ''
        if not phone:
            continue
        try:
            if client is None:
                # Dry run: pretend to send
                results.append({
                    'phone': phone,
                    'name': name,
                    'status': 'dry-run',
                    'message': message
                })
            else:
                msg = client.messages.create(
                    to=phone,
                    from_=cfg.from_number,
                    body=message
                )
                results.append({
                    'phone': phone,
                    'name': name,
                    'status': 'sent',
                    'sid': getattr(msg, 'sid', None)
                })
        except Exception as e:
            results.append({
                'phone': phone,
                'name': name,
                'status': 'error',
                'error': str(e)
            })

    summary = {
        'count': len(results),
        'dry_run': client is None,
        'results': results,
        'timestamp': datetime.now().isoformat()
    }
    return summary


def format_glucose_alert_sms(payload: Dict[str, Any]) -> str:
    """Create a concise SMS message for a glucose alert payload from glucose_monitor."""
    level = payload.get('level', 'alert').upper()
    value = payload.get('value')
    threshold = payload.get('threshold')
    ts = payload.get('timestamp')
    suggestion = payload.get('suggestion')
    suggestion_short = suggestion
    if suggestion:
        # Keep SMS short
        suggestion_short = suggestion.strip()
        if len(suggestion_short) > 200:
            suggestion_short = suggestion_short[:197] + '...'

    parts = [f"{level} GLUCOSE: {value} mg/dL", f"Threshold: {threshold}", f"At: {ts}"]
    if suggestion_short:
        parts.append(f"Note: {suggestion_short}")
    return ' | '.join([p for p in parts if p])


def send_glucose_alert(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Format and send a glucose alert payload as SMS to all recipients."""
    message = format_glucose_alert_sms(payload)
    return send_sms_to_all(message)
