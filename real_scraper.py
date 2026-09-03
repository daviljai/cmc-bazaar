import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.craftersmc.net/v1"

headers = {
    "X-API-Key": API_KEY
}

DATA_FOLDER = "data"
MAX_ENTRIES = 3200

os.makedirs(DATA_FOLDER, exist_ok=True)

# GET ITEM LIST
items_url = f"{BASE_URL}/resources/skyblock/bazaar/items"

items_response = requests.get(
    items_url,
    headers=headers,
    timeout=20
)

print("ITEM STATUS:", items_response.status_code)

if items_response.status_code != 200:
    print("API ERROR BODY:", items_response.text[:2000])
    print("API KEY PRESENT:", bool(API_KEY))
    print("API KEY LENGTH:", len(API_KEY) if API_KEY else 0)
    raise SystemExit(1)

items_data = items_response.json()
items = items_data["items"]

# SAVE ITEM LIST
with open(f"{DATA_FOLDER}/all_items.json", "w") as f:
    json.dump(items, f, indent=4)

print("TOTAL ITEMS:", len(items))

# SCAN ITEMS
for item in items:
    while True:
        try:
            print("Fetching:", item)

            url = f"{BASE_URL}/skyblock/bazaar/{item}/details"
            response = requests.get(url, headers=headers, timeout=20)

            print("STATUS:", response.status_code)

            if response.status_code == 429:
                print("RATE LIMITED - waiting 15 sec")
                time.sleep(15)
                continue

            if response.status_code != 200:
                print("API ERROR BODY:", response.text[:1000])
                print("Skipping:", item)
                break

            data = response.json()

            if not data.get("success"):
                print("Invalid data:", item)
                break

            entry = {
                "time": int(time.time()),
                "data": data
            }

            path = f"{DATA_FOLDER}/{item}.json"

            if os.path.exists(path):
                with open(path, "r") as f:
                    try:
                        history = json.load(f)
                    except Exception:
                        history = []
            else:
                history = []

            if not isinstance(history, list):
                history = []

            history.append(entry)
            history = history[-MAX_ENTRIES:]

            with open(path, "w") as f:
                json.dump(history, f, indent=4)

            print("Saved:", path)
            time.sleep(1)
            break

        except Exception as e:
            print("ERROR:", item, e)
            time.sleep(5)

print("SCAN COMPLETE")
