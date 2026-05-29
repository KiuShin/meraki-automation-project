import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MERAKI_API_KEY")
BASE_URL = "https://api.meraki.com/api/v1"

HEADERS = {
    "X-Cisco-Meraki-API-Key": API_KEY,
    "Content-Type": "application/json"
}

if not API_KEY:
    raise ValueError("MERAKI_DASHBOARD_API_KEY environment variable not set")