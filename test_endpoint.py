import requests
import json

# Test the endpoint
url = "http://localhost:5174/get-report-data"
payload = {"patient_id": 1}
headers = {"Content-Type": "application/json"}

# Send the request
response = requests.post(url, json=payload, headers=headers)

# Print status and response
print(f"Status code: {response.status_code}")
try:
    data = response.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error parsing JSON: {e}")
    print(response.text)