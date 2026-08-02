import urllib3
import requests
import json

urllib3.disable_warnings()

url = "https://stampede3.tacc.utexas.edu:60098/v1/models"
headers = {
    "Authorization": "Bearer flexserv",
    "x-flexserv-token": "flexserv",
    "x-flexserv-secret": "flexserv"
}

try:
    print("Testing GET /v1/models on port 60098...")
    response = requests.get(url, headers=headers, verify=False, timeout=10)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
