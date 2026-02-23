
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://doadmin:485093A7X1wL2GvS@NX-REPO-DB-0761394b.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("SUCCESS: Connected to MongoDB")
except Exception as e:
    print(f"FAILURE: {e}")
