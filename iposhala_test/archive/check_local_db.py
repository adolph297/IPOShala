
from pymongo import MongoClient
import os

uri = "mongodb://localhost:27017"
client = MongoClient(uri)
db = client["ippo_shala"] # Typos? User said iposhala or ipo_shala?
# debug_startup.py said DB_NAME = iposhala
db = client["iposhala"]
coll = db["ipo_past_master"]
count = coll.count_documents({})
print(f"Local DB 'iposhala' count: {count}")

# Check other names
db2 = client["ipo_shala"]
count2 = db2["ipo_past_master"].count_documents({})
print(f"Local DB 'ipo_shala' count: {count2}")
