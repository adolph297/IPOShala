import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "iposhala")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
coll = db["ipo_past_master"]

symbols = ["E2ERAIL", "SAMPOORNA", "MARUSHIKA"]

print("--- VERIFYING OFFICIAL DATA ---")
for s in symbols:
    doc = coll.find_one({"symbol": s})
    if doc:
        print(f"{s}:")
        print(f"  Official Issue Size: {doc.get('official_issue_size')}")
        print(f"  Official Lot Size:   {doc.get('official_lot_size')}")
        print(f"  Stored Issue Size:   {doc.get('issue_size')}")
        print(f"  Stored Lot Size:     {doc.get('lot_size')}")
    else:
        print(f"{s}: Not found in database.")
