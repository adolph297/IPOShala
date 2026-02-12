
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "iposhala")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

symbol = "E2ERAIL"

print(f">>> Checking 'ipo_master' for {symbol} <<<")
if "ipo_master" in db.list_collection_names():
    doc = db.ipo_master.find_one({"symbol": symbol})
    if doc:
        print(f"Found {symbol} in ipo_master!")
        import pprint
        pprint.pprint(list(doc.keys()))
        # Check for nse_company
        if "nse_company" in doc:
            print("Has nse_company data.")
            ann = (doc["nse_company"] or {}).get("announcements")
            print(f"Announcements type: {type(ann)}")
        else:
            print("No nse_company in ipo_master doc.")
    else:
        print(f"{symbol} NOT found in ipo_master.")
else:
    print("'ipo_master' collection does not exist.")

print(f"\n>>> Checking 'ipo_past_master' for {symbol} <<<")
doc_past = db.ipo_past_master.find_one({"symbol": symbol})
if doc_past:
    print(f"Found {symbol} in ipo_past_master.")
    ann = (doc_past.get("nse_company") or {}).get("announcements")
    from iposhala_test.api.routes.company import unwrap_section
    items = unwrap_section(ann)
    print(f"Announcements count (unwrapped): {len(items)}")
else:
    print(f"{symbol} NOT found in ipo_past_master.")
