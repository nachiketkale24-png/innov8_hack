import requests
import json

# Test root endpoint
print("Testing GET /")
response = requests.get("http://127.0.0.1:8000/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test process endpoint
print("Testing POST /process")
payload = {
    "query": "schemes for farmers",
    "user": {
        "income": 150000,
        "occupation": "farmer",
        "documents": ["Aadhar"]
    }
}

response = requests.post("http://127.0.0.1:8000/process", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
