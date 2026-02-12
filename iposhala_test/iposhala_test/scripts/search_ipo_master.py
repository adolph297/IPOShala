
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

print(">>> Searching for 'ipo_master' in ALL databases <<<")

dbs = client.list_database_names()
print(f"Databases found: {dbs}")

found = False
for db_name in dbs:
    db = client[db_name]
    cols = db.list_collection_names()
    if "ipo_master" in cols:
        print(f"\n[FOUND] 'ipo_master' exists in database: {db_name}")
        count = db.ipo_master.count_documents({})
        print(f"Record count: {count}")
        sample = db.ipo_master.find_one()
        import pprint
        pprint.pprint(sample)
        found = True

if not found:
    print("\n[NOT FOUND] 'ipo_master' collection not found in any database.")
    # Show counts for ipo_past_master in iposhala just in case
    db_iposhala = client['iposhala']
    if 'ipo_past_master' in db_iposhala.list_collection_names():
        print(f"\nInfo: 'ipo_past_master' in 'iposhala' has {db_iposhala.ipo_past_master.count_documents({})} records.")
