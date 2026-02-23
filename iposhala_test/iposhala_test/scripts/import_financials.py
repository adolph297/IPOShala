import json
import os
import sys
from datetime import datetime
from pymongo import MongoClient, UpdateOne

# Add project root to path
sys.path.append(os.getcwd())

# Config
BASE_DIR = os.getcwd()
JSON_FILE = os.path.join(BASE_DIR, "batch_5_financials.json")
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "iposhala"
COLLECTION = "ipo_past_master"

def run():
    if not os.path.exists(JSON_FILE):
        print(f"Error: JSON file not found at {JSON_FILE}")
        return

    print(f"Reading {JSON_FILE}...")
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} companies to import.")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION]

    ops = []
    
    for symbol, content in data.items():
        if not content: continue
        
        financials = content.get("audited_financials", [])
        website = content.get("website")
        
        # Split into Annual and Quarterly
        annual_reports = []
        financial_results = []
        
        for item in financials:
            # Common structure
            doc = {
                "desc": item.get("label", item.get("type")),
                "url": item.get("url"),
                "source": "scraped",
                "imported_at": datetime.now().isoformat()
            }
            
            if item.get("type") == "Annual Report":
                doc["m_yr"] = item.get("year", "")
                annual_reports.append(doc)
            else:
                # Quarterly / Financial Results
                doc["period"] = item.get("period", "")
                if item.get("year"):
                    doc["year"] = item.get("year")
                financial_results.append(doc)
                
        # Prepare Update
        update_fields = {}
        
        if website:
            update_fields["website"] = website
            
        if annual_reports:
            # We overwrite annual_reports for now as our source is likely better than empty/broken NSE data
            # But we might want to check if it exists? 
            # For this task, let's assume replacement is fine as per user goal to "Show data"
            update_fields["nse_company.annual_reports"] = {
                "__available__": True,
                "data": annual_reports 
            }
            
        if financial_results:
             update_fields["nse_company.financial_results"] = {
                "__available__": True,
                "data": financial_results
            }
            
        # Also store raw for backup
        update_fields["nse_company.extracted_financials"] = financials

        if update_fields:
            ops.append(
                UpdateOne(
                    {"symbol": symbol},
                    {"$set": update_fields}
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
