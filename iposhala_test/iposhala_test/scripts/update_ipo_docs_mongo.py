import csv
from datetime import datetime
from pymongo import MongoClient

# ---- CONFIG ----

MONGO_URI = "mongodb://localhost:27017"  # change if needed
DB_NAME = "iposhala"
COLLECTION = "ipo_past_master"

INPUT = "iposhala_test/iposhala_test/data/IPO_bidding_centers_updated.csv"

# ----------------

client = MongoClient(MONGO_URI)
col = client[DB_NAME][COLLECTION]

DOC_MAP = {
    "doc_rhp": "rhp",
    "doc_ratios": "ratios",
    "doc_bidding": "bidding-centers",
    "doc_forms": "forms",
    "doc_security_pre": "pre-anchor",
    "doc_security_post": "post-anchor",
    "Anchor_Allocation_ZIP": "anchor-allocation",
}

now = datetime.utcnow()

def build_doc_entry(url):
    return {
        "available": bool(url),
        "source_url": url if url else None,
        "updated_at": now,
    }

with open(INPUT, newline="", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    for row in reader:

        symbol = row.get("Symbol")

        if not symbol:
            continue

        ipo_docs = {}

        for csv_col, mongo_key in DOC_MAP.items():

            url = row.get(csv_col, "").strip()

            ipo_docs[mongo_key] = build_doc_entry(url)

        update_payload = {
            "$set": {
                "ipo_docs": ipo_docs,
                "ipo_docs_last_updated": now
            }
        }

        result = col.update_one(
            {"symbol": symbol.upper()},
            update_payload
        )

        print(f"{symbol} → updated ({result.modified_count})")

print("\n✅ Mongo IPO docs update complete")
