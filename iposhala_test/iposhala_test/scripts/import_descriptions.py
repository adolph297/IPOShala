import os
import sys
import pandas as pd
from pymongo import MongoClient, UpdateOne

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, "data", "company_descriptions.csv")
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "iposhala"
COLLECTION = "ipo_past_master"

def run():
    if not os.path.exists(CSV_FILE):
        print(f"Error: CSV file not found at {CSV_FILE}")
        return

    print(f"Reading {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE)
    
    # Filter rows with descriptions
    df = df[df["description"].notna() & (df["description"] != "")]
    print(f"Found {len(df)} descriptions to import.")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION]

    ops = []
    
    for _, row in df.iterrows():
        symbol = row.get("Symbol")
        desc = row.get("description")
        company_name = row.get("Company Name")
        
        if not symbol or pd.isna(symbol):
            # Try to find by company name if symbol is missing (unlikely in our data but safe)
            # Actually, let's skip for now as Symbol is primary key in our logic
            print(f"Skipping {company_name} - No Symbol")
            continue
            
        ops.append(
            UpdateOne(
                {"symbol": symbol},
                {"$set": {"description": desc}}
            )
        )
        
    if ops:
        print(f"Executing {len(ops)} updates...")
        result = collection.bulk_write(ops)
        print(f"Updates: {result.modified_count}, Matched: {result.matched_count}")
    else:
        print("No updates to perform.")

if __name__ == "__main__":
    run()
