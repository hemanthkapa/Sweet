#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime

# Ensure src/ is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
sys.path.insert(0, SRC_DIR)

import notifications as notif  # noqa: E402


def test_format_glucose_alert_sms_truncates():
    long_note = "A" * 500
    payload = {
        'level': 'high',
        'value': 300,
        'threshold': 250,
        'timestamp': datetime.now().isoformat(),
        'suggestion': long_note,
    }
    msg = notif.format_glucose_alert_sms(payload)
    assert '...' in msg
    # message should be reasonably short for SMS
    assert len(msg) < 300


def test_list_recipients_merges_env_and_file(tmp_path, monkeypatch):
    # prepare file recipients
    data = [
        {"name": "Alice", "phone": "+15550000001"}
    ]
    file_path = tmp_path / 'recipients.json'
    file_path.write_text(json.dumps(data), encoding='utf-8')

    # env config
    monkeypatch.setenv('ALERT_RECIPIENTS_FILE', str(file_path))
    monkeypatch.setenv('ALERT_RECIPIENTS', '+15550000002,+15550000001')  # contains duplicate

    recips = notif.list_recipients()
    phones = sorted([r['phone'] for r in recips])

    # Should contain both numbers with duplicate deduped
    assert "+15550000001" in phones
    assert "+15550000002" in phones
    assert len(phones) == 2
