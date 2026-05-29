import logging
import json
from datetime import datetime

# Set up the logger to write to a file

logging.basicConfig(
    filename='maraki_audit.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

def log_structured_health(device_list):
    """
    Parses the raw Meraki JSON and writes structured entries to a log file
    """
    for device in device_list:
        model = device.get('model', 'Unknown Model')
        status = device.get('status', 'Unknown Status')

        # Create a structured data packet
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "serial": device.get('serial', 'Unknown Serial'),
            "model": model,
            "status": status,
            "last_seen": device.get('lastReportedAt'),
            "is_target": "MX68" in str(model)
        }

        # 1. Log to the file for long-term storage (JSON format)
        logging.info(json.dumps(log_entry))

        # 2. Clean CLI feedback for you to watch life
        if log_entry['status'] == 'online':
            print(f" ALERT: {model} ({log_entry['serial']}) is {status.upper()}")
        else:
            print(f"{model} is healthy.")