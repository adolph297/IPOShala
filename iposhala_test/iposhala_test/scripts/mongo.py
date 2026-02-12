
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# ALWAYS load .env from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

ipo_past_master = db["ipo_past_master"]
ipo_past_issue_info = db["ipo_past_issue_info"]
ipo_live_upcoming = db["ipo_live_upcoming"]
ipo_master = db["ipo_master"]


print("MONGO_URI =", MONGO_URI)
print("DB_NAME =", DB_NAME)
print("CLIENT ADDRESS =", client.address)
print("DB USED =", db.name)
