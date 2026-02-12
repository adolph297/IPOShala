
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import pprint

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

print(f"MONGO_URI: {MONGO_URI}")
dbs = client.list_database_names()
print(f"Databases: {dbs}")

found_any = False

for db_name in dbs:
    if db_name in ['admin', 'config', 'local']: continue
    db = client[db_name]
    print(f"\n--- Database: {db_name} ---")
    
    for col_name in db.list_collection_names():
        # Search for E2ERAIL
        doc = db[col_name].find_one({"symbol": "E2ERAIL"})
        if doc:
            found_any = True
            print(f"  [FOUND] E2ERAIL in collection: {col_name}")
            
            # Check for announcements
            ann = None
            if 'nse_company' in doc:
                ann = (doc['nse_company'] or {}).get('announcements')
            elif 'announcements' in doc:
                ann = doc['announcements']
                
            if ann:
                payload = []
                if isinstance(ann, dict): payload = ann.get('payload') or []
                elif isinstance(ann, list): payload = ann
                print(f"    - Announcements count: {len(payload)}")
            else:
                print("    - No announcements field found in this document.")

        # Also search for ANY document with announcements to see if we're in the right place
        doc_with_ann = db[col_name].find_one({
            "$or": [
                {"nse_company.announcements.payload": {"$exists": True, "$not": {"$size": 0}}},
                {"announcements": {"$exists": True, "$not": {"$size": 0}}}
            ]
        })
        if doc_with_ann:
            print(f"  [INFO] Collection {col_name} HAS documents with data. Example symbol: {doc_with_ann.get('symbol')}")

if not found_any:
    print("\n[FAILED] Could not find 'E2ERAIL' in any non-system collection.")
