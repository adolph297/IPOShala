
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = "mongodb://localhost:27017" # Hardcoded to be sure
client = MongoClient(MONGO_URI)

print(f">>> CRITICAL DATABASE SCAN <<<")

all_dbs = client.list_database_names()
print(f"Databases: {all_dbs}")

for db_name in all_dbs:
    db = client[db_name]
    print(f"\n--- Checking DB: {db_name} ---")
    cols = db.list_collection_names()
    print(f"Collections: {cols}")
    
    if "ipo_master" in cols:
        print(f"!!! FOUND 'ipo_master' in {db_name} !!!")
        count = db.ipo_master.count_documents({})
        print(f"Total records: {count}")
        if count > 0:
            sample = db.ipo_master.find_one()
            print(f"Sample symbol: {sample.get('symbol')}")
            # Check for E2ERAIL specifically
            e2 = db.ipo_master.find_one({"symbol": "E2ERAIL"})
            if e2:
                print(f"Found E2ERAIL in {db_name}.ipo_master!")
                ann = (e2.get("nse_company") or {}).get("announcements")
                if ann:
                    print("Has nse_company.announcements")
    
    # Check if ANY collection has E2ERAIL with announcements
    for col in cols:
        try:
            doc = db[col].find_one({"symbol": "E2ERAIL"})
            if doc:
                nse = doc.get("nse_company") or {}
                ann = nse.get("announcements")
                if ann:
                    # check if it has payload
                    payload = []
                    if isinstance(ann, dict): payload = ann.get("payload") or []
                    elif isinstance(ann, list): payload = ann
                    if len(payload) > 0:
                        print(f"!!! [SUCCESS] Found E2ERAIL with {len(payload)} announcements in {db_name}.{col} !!!")
        except:
            pass
