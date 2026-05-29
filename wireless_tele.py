import requests

def get_wireless_latency(target_url, auth_headers):
    """
    Accpets the pre-built URL and headers from the main app.
    Focuses purely on the Request/Response and data extration.
    """

    response = requests.get(target_url, headers=auth_headers)

    if response.status_code == 200:
        return response.json()
    return []