
import os
from datetime import datetime, timezone
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "iposhala")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
ipo_past_master = db["ipo_past_master"]

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nseindia.com/",
}

def fetch_announcements(symbol):
    print(f"Fetching announcements for {symbol}...")
    
    s = requests.Session()
    s.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10) # warmup
    
    for index in ['equities', 'sme']:
        url = f"https://www.nseindia.com/api/corporate-announcements?index={index}&symbol={symbol}"
        print(f"  Checking index: {index}...")
        res = s.get(url, headers=NSE_HEADERS, timeout=20)
        if res.status_code != 200:
            continue
        
        data = res.json()
        items = []
        if isinstance(data, list): items = data
        elif isinstance(data, dict): items = data.get("data") or []
        
        filtered = [x for x in items if (x.get("symbol") or "").upper() == symbol]
        if filtered:
            return filtered
            
    return []

def run():
    symbol = "E2ERAIL"
    items = fetch_announcements(symbol)
    print(f"Found {len(items)} announcements.")
    
    if len(items) > 0:
        ann = {
            "available": True,
            "payload": items,
            "source_url": f"https://www.nseindia.com/api/corporate-announcements?index=equities&symbol={symbol}"
        }
        
        db["ipo_past_master"].update_one(
            {"symbol": symbol},
            {"$set": {
                "nse_company.announcements": ann,
                "nse_company_updated_at": datetime.now(timezone.utc),
                "nse_company_fetched": True
            }}
        )
        print("✅ Data updated in DB.")
        
        # ALSO: Create ipo_master if the user insists
        print("Creating 'ipo_master' collection and inserting this doc...")
        doc = db["ipo_past_master"].find_one({"symbol": symbol})
        if doc:
            doc.pop("_id", None)
            db["ipo_master"].update_one({"symbol": symbol}, {"$set": doc}, upsert=True)
            print("✅ Data mirrored to 'ipo_master'.")
    else:
        print("❌ No data found on NSE for this symbol.")

if __name__ == "__main__":
    run()
