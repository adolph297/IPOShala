
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

print(f"URL: {MONGO_URI}")
for db_name in client.list_database_names():
    if db_name in ['admin', 'config', 'local']: continue
    db = client[db_name]
    print(f"\nDB: {db_name}")
    for col in db.list_collection_names():
        count = db[col].count_documents({})
        print(f"  - {col}: {count} docs")
        if count > 0:
            sample = db[col].find_one()
            if 'symbol' in sample:
                print(f"    Example symbol: {sample['symbol']}")
