
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Add the current directory to sys.path to find scripts.mongo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "iposhala")

print(f"Connecting to {MONGO_URI}, DB: {DB_NAME}")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("Collections in database:")
print(db.list_collection_names())

if "ipo_master" in db.list_collection_names():
    print("\nSample document from ipo_master:")
    sample = db.ipo_master.find_one()
    import pprint
    pprint.pprint(sample)
else:
    print("\nCollection 'ipo_master' NOT found!")
    # Check for similar names
    ipo_collections = [c for c in db.list_collection_names() if "ipo" in c.lower()]
    print(f"IPO-related collections: {ipo_collections}")

