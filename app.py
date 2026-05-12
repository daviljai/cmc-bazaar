import requests
import sqlite3
import threading
import time
import os

from dotenv import load_dotenv
from flask import Flask, render_template, jsonify

load_dotenv()

BASE_URL = "https://api.craftersmc.net/v1"

API_KEY = os.getenv("API_KEY")

headers = {
    "X-API-Key": API_KEY
}

app = Flask(__name__)

# =========================
# DATABASE
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "bazaar.db")

db = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

db.execute("PRAGMA journal_mode=WAL")

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bazaar (
    timestamp INTEGER,
    item TEXT,

    buy1_price REAL,
    buy1_qty INTEGER,

    buy2_price REAL,
    buy2_qty INTEGER,

    buy3_price REAL,
    buy3_qty INTEGER,

    buy4_price REAL,
    buy4_qty INTEGER,

    buy5_price REAL,
    buy5_qty INTEGER,

    buy6_price REAL,
    buy6_qty INTEGER,

    buy7_price REAL,
    buy7_qty INTEGER,

    buy8_price REAL,
    buy8_qty INTEGER,

    sell1_price REAL,
    sell1_qty INTEGER,

    sell2_price REAL,
    sell2_qty INTEGER,

    sell3_price REAL,
    sell3_qty INTEGER,

    sell4_price REAL,
    sell4_qty INTEGER,

    sell5_price REAL,
    sell5_qty INTEGER,

    sell6_price REAL,
    sell6_qty INTEGER,

    sell7_price REAL,
    sell7_qty INTEGER,

    sell8_price REAL,
    sell8_qty INTEGER,

    buy_volume INTEGER,
    sell_volume INTEGER
)
""")

db.commit()

# =========================
# GET ITEM LIST
# =========================

def get_items():

    try:

        url = f"{BASE_URL}/resources/skyblock/bazaar/items"

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        print("ITEM STATUS:", response.status_code)

        if response.status_code != 200:
            return []

        data = response.json()

        return data.get("items", [])

    except Exception as e:

        print("GET ITEMS ERROR:", e)

        return []

# =========================
# GET ITEM DATA
# =========================

def get_item_data(item):

    url = f"{BASE_URL}/skyblock/bazaar/{item}/details"

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    print("STATUS:", response.status_code)

    # RATE LIMITED
    if response.status_code == 429:

        retry = int(
            response.headers.get(
                "Retry-After",
                15
            )
        )

        print("RATE LIMITED - waiting", retry, "sec")

        time.sleep(retry)

        return None

    # BAD RESPONSE
    if response.status_code != 200:
        return None

    try:
        return response.json()

    except Exception:
        return None

# =========================
# LIMIT DATABASE SIZE
# =========================

def trim_old_data(item):

    cursor.execute("""
    DELETE FROM bazaar
    WHERE rowid NOT IN (
        SELECT rowid
        FROM bazaar
        WHERE item=?
        ORDER BY timestamp DESC
        LIMIT 3000
    )
    AND item=?
    """, (item, item))

    db.commit()

# =========================
# SCRAPER
# =========================

def scraper():

    while True:

        try:

            items = get_items()

            print("TOTAL ITEMS:", len(items))

            for item in items:

                try:

                    print("Fetching:", item)

                    data = get_item_data(item)

                    # failed request
                    if not data:
                        continue

                    if "buyTopEntries" not in data:
                        continue

                    if "sellTopEntries" not in data:
                        continue

                    if not data["buyTopEntries"]:
                        continue

                    if not data["sellTopEntries"]:
                        continue

                    buy_entries = data["buyTopEntries"][:8]
                    sell_entries = data["sellTopEntries"][:8]

                    while len(buy_entries) < 8:
                        buy_entries.append({
                            "price": 0,
                            "quantity": 0
                        })

                    while len(sell_entries) < 8:
                        sell_entries.append({
                            "price": 0,
                            "quantity": 0
                        })

                    buy_volume = data.get("buyVolume", 0)
                    sell_volume = data.get("sellVolume", 0)

                    timestamp = int(time.time())

                    values = [
                        timestamp,
                        item
                    ]

                    for entry in buy_entries:

                        values.append(entry["price"])
                        values.append(entry["quantity"])

                    for entry in sell_entries:

                        values.append(entry["price"])
                        values.append(entry["quantity"])

                    values.append(buy_volume)
                    values.append(sell_volume)

                    cursor.execute(f"""
                    INSERT INTO bazaar
                    VALUES ({",".join(["?"] * len(values))})
                    """, values)

                    db.commit()

                    # keep latest 3000 only
                    trim_old_data(item)

                    print("Saved:", item)

                    # delay between requests
                    time.sleep(5)

                except Exception as e:

                    print("ITEM ERROR:", item, e)

            print("\nSCAN COMPLETE")
            print("WAITING 10 MINUTES...\n")

            # WAIT 10 MINUTES
            time.sleep(600)

        except Exception as e:

            print("MAIN LOOP ERROR:", e)

            time.sleep(10)

# =========================
# HOME
# =========================

@app.route("/")
def home():

    items = get_items()

    items.sort()

    return render_template(
        "index.html",
        items=items
    )

# =========================
# API
# =========================

@app.route("/api/<item>")
def api(item):

    cursor.execute("""
    SELECT *
    FROM bazaar
    WHERE item=?
    ORDER BY timestamp ASC
    LIMIT 3000
    """, (item,))

    rows = cursor.fetchall()

    data = []

    for row in rows:

        data.append({

            "time": row[0],
            "item": row[1],

            "buy1_price": row[2],
            "buy1_qty": row[3],

            "buy2_price": row[4],
            "buy2_qty": row[5],

            "buy3_price": row[6],
            "buy3_qty": row[7],

            "buy4_price": row[8],
            "buy4_qty": row[9],

            "buy5_price": row[10],
            "buy5_qty": row[11],

            "buy6_price": row[12],
            "buy6_qty": row[13],

            "buy7_price": row[14],
            "buy7_qty": row[15],

            "buy8_price": row[16],
            "buy8_qty": row[17],

            "sell1_price": row[18],
            "sell1_qty": row[19],

            "sell2_price": row[20],
            "sell2_qty": row[21],

            "sell3_price": row[22],
            "sell3_qty": row[23],

            "sell4_price": row[24],
            "sell4_qty": row[25],

            "sell5_price": row[26],
            "sell5_qty": row[27],

            "sell6_price": row[28],
            "sell6_qty": row[29],

            "sell7_price": row[30],
            "sell7_qty": row[31],

            "sell8_price": row[32],
            "sell8_qty": row[33],

            "buy_volume": row[34],
            "sell_volume": row[35]
        })

    return jsonify(data)

# =========================
# START
# =========================

if __name__ == "__main__":

    threading.Thread(
        target=scraper,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
        use_reloader=False
    )
