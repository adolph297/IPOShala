from pymongo import MongoClient
import os

MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["iposhala"]
coll = db["ipo_past_master"]

symbol = "SMC"
doc = coll.find_one({"symbol": symbol})

if doc:
    print(f"Found {symbol}: {doc.get('company_name')}")
else:
    print(f"{symbol} not found in DB.")
    # Try fuzzy search
    doc = coll.find_one({"company_name": {"$regex": "SMC", "$options": "i"}})
    if doc:
        print(f"Found alternative match: {doc.get('symbol')} - {doc.get('company_name')}")
