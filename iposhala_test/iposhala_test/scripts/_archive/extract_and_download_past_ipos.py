import os
import pandas as pd
from pymongo import MongoClient

CSV_FILE = "data/IPO-PastIssue-13-Jan-2026.csv"
BASE_DIR = "nse_ipo_docs"

# MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client.iposhala
collection = db.past_ipo_links

os.makedirs(BASE_DIR, exist_ok=True)

df = pd.read_csv(CSV_FILE)

def safe_name(name):
    return (
        name.strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("&", "AND")
    )

print("Processing IPOs...")

for _, row in df.iterrows():
    company = row["COMPANY NAME"]
    symbol = row["Symbol"]

    folder_name = safe_name(company)
    folder_path = os.path.join(BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Candidate NSE archive links (no API)
    links = [
        f"https://nsearchives.nseindia.com/content/ipo/{symbol}_RHP.pdf",
        f"https://nsearchives.nseindia.com/content/ipo/{symbol}_Prospectus.pdf",
    ]

    collection.update_one(
        {"symbol": symbol},
        {
            "$set": {
                "company": company,
                "symbol": symbol,
                "folder": folder_path,
                "candidate_links": links
            }
        },
        upsert=True
    )

print("✅ Folder structure created")
print("✅ Links stored in MongoDB (past_ipo_links)")
