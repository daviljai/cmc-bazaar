import cloudscraper
import json
import os
import time

BASE_URL = "https://api.craftersmc.net/v1"

API_KEY = os.getenv("API_KEY")

headers = {
    "X-API-Key": API_KEY
}

scraper = cloudscraper.create_scraper()

# CREATE DATA FOLDER
os.makedirs("data", exist_ok=True)

# GET ITEM LIST
items_url = f"{BASE_URL}/resources/skyblock/bazaar/items"

response = scraper.get(
    items_url,
    headers=headers
)

print("ITEM STATUS:", response.status_code)

data = response.json()

items = data.get("items", [])

print("TOTAL ITEMS:", len(items))

# SAVE ITEM LIST
with open("data/all_items.json", "w") as f:
    json.dump(items, f, indent=4)

# FETCH EACH ITEM
for item in items:

    while True:

        try:

            print("Fetching:", item)

            item_url = f"{BASE_URL}/skyblock/bazaar/{item}/details"

            response = scraper.get(
                item_url,
                headers=headers
            )

            print("STATUS:", response.status_code)

            # RATE LIMITED
            if response.status_code == 429:

                print("RATE LIMITED - waiting 15 sec")
                time.sleep(15)
                continue

            item_data = response.json()

            output = {
                "time": int(time.time()),
                "item": item,
                "data": item_data
            }

            file_path = f"data/{item}.json"

            with open(file_path, "w") as f:
                json.dump(output, f, indent=4)

            print("Saved:", file_path)

            # NORMAL DELAY
            time.sleep(3)

            break

        except Exception as e:

            print("ERROR:", item, e)

            time.sleep(10)
