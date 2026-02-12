
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

print(f">>> Searching for 'E2ERAIL' with data in ALL databases <<<")

dbs = client.list_database_names()
for db_name in dbs:
    db = client[db_name]
    for col_name in db.list_collection_names():
        doc = db[col_name].find_one({"symbol": "E2ERAIL"})
        if doc:
            print(f"\n[FOUND] 'E2ERAIL' in {db_name}.{col_name}")
            # Check for any field that looks like announcements or corporate data
            data_fields = [k for k in doc.keys() if any(x in k.lower() for x in ['announc', 'corp', 'nse', 'master'])]
            print(f"Relevant fields: {data_fields}")
            
            # Specifically check if nse_company has data here
            if 'nse_company' in doc:
                ann = (doc['nse_company'] or {}).get('announcements')
                if ann:
                   print(f"Has nse_company.announcements: {type(ann)}")
                   if isinstance(ann, dict) and ann.get('payload'):
                       print(f"Announcement Payload Count: {len(ann['payload'])}")
                   elif isinstance(ann, list):
                       print(f"Announcement List Count: {len(ann)}")
            
            # Check for generic 'announcements' top level
            if 'announcements' in doc:
                print(f"Has top-level announcements: {type(doc['announcements'])}")

print("\n>>> Listing all collections across all DBs for comparison <<<")
for db_name in dbs:
    print(f"{db_name}: {client[db_name].list_collection_names()}")
