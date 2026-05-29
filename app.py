import requests
import os
import json
# Initialize environment and constants
from config import HEADERS, BASE_URL
from logger import  log_structured_health
from wireless_tele import get_wireless_latency


# =============================
# Logging and Data Handling
# =============================

# HTTP Requests and Data Handling
def send_meraki_request(endpoint, headers, method='GET', payload=None, params=None):
    """
    A unified wrapper to handle all outbound API communication.
    Centralizes error handling, timeouts, and URL construction.
    """
    #print(f"DEBUG -> RAW BASE_URL FROM CONFIG:  '{BASE_URL}'")
    #print(f"DEBUG -> RAW ENDPOINT FROM WORKER:  '{endpoint}'")
   # print(f"DEBUG -> COMPILED OUTBOUND URL:     '{f'{BASE_URL}/{endpoint.lstrip('/')}'}'")
    #import sys; sys.exit("🛑 Hard stopping engine for URL verification.")
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"

    try:
        response = requests.request(method, url, headers=headers, json=payload, params=params,timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f" HTTP error occurred for endpoint [{endpoint}]: {http_err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Request error for endpoint [{endpoint}]: {err}")
        return None
    
        
#GET ORG ID
def get_org_id(headers):
    """Fetches the first available Organization ID."""
    data = send_meraki_request("/organizations", headers)
    return data[0]["id"] if data else None
    
    
def get_net_id(org_id, auth_headers):
	"""Fetches the first available Network ID within the specified Org."""
	response = requests.get(f"{BASE_URL}/organizations/{org_id}/networks", headers=auth_headers)
	
	if response.status_code == 200:
		networks = response.json()
		if not networks:
			print("❌ No networks found in this organization.")
			return None
		
		# Pulling details from the first network
		net_id = networks[0]["id"]
		net_name = networks[0]["name"]
		print(f"✅ Connected to Network: {net_name} (ID: {net_id})")
		return net_id
	else:
		print(f"❌ Failed to fetch Network. Status: {response.status_code}")
		return None
     

def get_net_id(org_id, headers):
    """
    Fetches the first available Network ID within the specified Org.
    """
    data = send_meraki_request(f"/organizations/{org_id}/networks", headers)

     #Pulling details from the first network
    net_id = data[0]["id"] if data else None
    net_name = data[0]["name"] if data else "N/A"
     
    if net_id:
        print(f"✅ Connected to Network: {net_name} (ID: {net_id})")
    else:
        print("❌ No networks found in this organization.")

    return net_id

# =============================
# Modules
# =============================


#CHECK DEVICE HEALTH
def check_device_health(org_id, headers):
    """
    Targets the stable GET /organizations/{orgId}/devices/statuses endpoint.
    This provides a snapshot of all hardware across the entire organization.
    """
    # In v1, we can use 'total_pages' to ensure we get every device
    query_params = {"total_pages": "all"}
    device_status = send_meraki_request(endpoint=f"/organizations/{org_id}/devices/statuses", headers=headers, params=query_params)
    
    print(f"\n--- v1 Org-Wide Device Audit ---")
    print(f"Total entries found: {len(device_status)}")
    
    for device in device_status:
        model = device.get('model', 'N/A')
        serial = device.get('serial', 'N/A')
        status = device.get('status', 'unknown') # online, offline, alerting, dormant
        
        # Pull the last check-in timestamp
        last_seen = device.get('lastReportedAt', 'Never')
        
        is_target = " ⭐ [TARGET]" if "MX68" in str(model) else ""
        
        print(f"Device: {model}{is_target}")
        print(f"Serial: {serial}")
        print(f"Connectivity: {status.upper()}")
        print(f"Last Heartbeat: {last_seen}")
        
        # Check if it's assigned to a network
        net_id = device.get('networkId')
        if net_id:
            print(f"Network: {net_id}")
        else:
            print("Status: Available in Inventory (Unassigned)")
            
        #print("-" * 30)
        
    return device_status   # Return the raw data for logging
    
# Log structured health data to a file and print alerts
def audit_org_inventory(org_id, headers):
    """Audits every piece of hardware owned by the Org, regardless of network assignment."""
    
    device_inventory = send_meraki_request(endpoint=f"/organizations/{org_id}/inventory/devices", headers=headers)

    print(f"\n--- Global Inventory Audit ({len(device_inventory)} items) ---")
        
    for item in device_inventory:
        model = item.get('model')
        serial = item.get('serial')
        assigned_net = item.get('networkId')
            
        status_label = "Assigned" if assigned_net else "Unassigned (Available)"
            
        print(f"Model: {model} | Serial: {serial}")
        print(f"Status: {status_label}")

        if assigned_net:
            print(f"Network ID: {assigned_net}")
        else:
             print(f"Inventory Result: Variable state is: {assigned_net}")
        print("-" * 30)
        


# --- MAIN EXECUTION---


if __name__ == "__main__":
    # Main Execution Flow
    my_org_id = get_org_id(HEADERS)
    my_net_id = get_net_id(my_org_id, HEADERS)
    if my_org_id:
        # Uncomment below if you want to run health check for the primary network
        check_device_health(my_org_id, HEADERS)        
        #Run log function for structured logging and store in variable
        inventory_data = check_device_health(my_org_id, HEADERS)
        
        if inventory_data:
            log_structured_health(inventory_data)
            print("\n Audit Log Updated: 'maraki_audit.log'")  # Confirmation of logging
         
        # Uncomment below if you want a full hardware audit
        audit_org_inventory(my_org_id, HEADERS)
        
#print(f"{my_org_id}, is the Org ID we are working with.")
#print(f"{my_net_id}, is the Network ID we are working with.")