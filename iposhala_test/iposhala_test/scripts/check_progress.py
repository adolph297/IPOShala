import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "iposhala")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
coll = db["ipo_past_master"]

total = coll.count_documents({})
fetched = coll.count_documents({"official_fetched_at": {"$exists": True}})
failed = coll.count_documents({"official_fetch_failed": True})
with_size = coll.count_documents({"official_issue_size": {"$exists": True, "$ne": None}})

print(f"Total IPOs: {total}")
print(f"Official Fetch Attempted: {fetched}")
print(f"Official Fetch Failed: {failed}")
print(f"Official Data Found: {with_size}")
