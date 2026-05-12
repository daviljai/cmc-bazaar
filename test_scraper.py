import json
import time

data = {
    "time": int(time.time()),
    "message": "github actions works"
}

with open("data/test.json", "w") as f:
    json.dump(data, f, indent=4)

print("Saved test data")