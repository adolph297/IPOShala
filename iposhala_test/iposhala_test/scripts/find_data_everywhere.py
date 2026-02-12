
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

print(f"Scanning all DBs on: {MONGO_URI}")

all_dbs = client.list_database_names()
for db_name in all_dbs:
    db = client[db_name]
    print(f"\nDB: {db_name}")
    try:
        cols = db.list_collection_names()
        for col_name in cols:
            count = db[col_name].count_documents({})
            print(f"  - {col_name}: {count} docs")
            # Search for E2ERAIL or GKSL
            doc = db[col_name].find_one({"symbol": {"$in": ["E2ERAIL", "GKSL"]}})
            if doc:
                print(f"    !!! FOUND SYMBOL {doc['symbol']} in {db_name}.{col_name} !!!")
                # check for announcements
                if 'nse_company' in doc:
                    ann = (doc.get('nse_company') or {}).get('announcements')
                    if ann:
                         items = []
                         if isinstance(ann, dict): items = ann.get('payload') or []
                         elif isinstance(ann, list): items = ann
                         print(f"    - Announcements count: {len(items)}")
                elif 'announcements' in doc:
                     ann = doc['announcements']
                     items = []
                     if isinstance(ann, dict): items = ann.get('payload') or []
                     elif isinstance(ann, list): items = ann
                     print(f"    - Announcements count: {len(items)}")
    except Exception as e:
        print(f"  Error accessing {db_name}: {e}")
