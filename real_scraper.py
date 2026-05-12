import requests
import json
import os
import time

BASE_URL = "https://api.craftersmc.net/v1"

API_KEY = os.getenv("API_KEY")

headers = {
    "X-API-Key": API_KEY
}

url = f"{BASE_URL}/resources/skyblock/bazaar/items"

response = requests.get(url, headers=headers)

print("STATUS:", response.status_code)

data = response.json()

items = data.get("items", [])

output = {
    "time": int(time.time()),
    "total_items": len(items),
    "items": items[:50]
}

os.makedirs("data", exist_ok=True)

with open("data/bazaar.json", "w") as f:
    json.dump(output, f, indent=4)

print("Saved bazaar.json")
