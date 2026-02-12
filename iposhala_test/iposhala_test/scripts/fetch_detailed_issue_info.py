import os
import sys
import time
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Add project root to path for local imports
sys.path.append(os.getcwd())

from iposhala_test.scrapers.nse_company_dynamic import cookie_pool

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "iposhala")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
coll = db["ipo_past_master"]

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.nseindia.com/",
}

def fetch_official_details(symbol, series="SME"):
    s = cookie_pool.get()
    
    # 1. Fetch Lot Size from ipo-master
    master_url = f"https://www.nseindia.com/api/ipo-master?symbol={symbol}"
    lot_size = None
    try:
        r = s.get(master_url, headers=NSE_HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # marketLot is typically the IPO lot size
            lot_size = data.get("marketLot")
    except Exception as e:
        print(f"Error fetching master for {symbol}: {e}")

    # 2. Fetch Issue Size from ipo-detail
    detail_url = f"https://www.nseindia.com/api/ipo-detail?symbol={symbol}&series={series}"
    issue_size = None
    try:
        r = s.get(detail_url, headers=NSE_HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # totalIssueSize in demandGraph is the official IPO size
            issue_size = data.get("demandGraph", {}).get("totalIssueSize")
            if not issue_size:
                issue_size = data.get("demandGraphALL", {}).get("totalIssueSize")
    except Exception as e:
        print(f"Error fetching detail for {symbol}: {e}")

    return lot_size, issue_size

def process_ipos(limit=2000):
    # Process IPOs that don't have official data yet OR failed previously (to retry once)
    query = {
        "official_fetched_at": {"$exists": False}
    }
    
    total_to_process = coll.count_documents(query)
    print(f"Found {total_to_process} IPOs needing official data.")
    
    cursor = coll.find(query).limit(limit)
    
    count = 0
    updated = 0
    failed = 0
    
    for doc in cursor:
        symbol = doc["symbol"]
        count += 1
        
        # Determine series from security_type or exchange
        sec_type = str(doc.get("security_type", "")).upper()
        series = "SME" if "SME" in sec_type else "EQ"
        
        print(f"\n[{count}/{total_to_process}] Processing {symbol} ({series})...")
        lot, size = fetch_official_details(symbol, series)
        
        if lot or size:
            update_data = {
                "official_lot_size": lot,
                "official_issue_size": size,
                "issue_size": size, 
                "lot_size": lot,    
                "official_fetched_at": datetime.utcnow()
            }
            coll.update_one({"symbol": symbol}, {"$set": update_data})
            print(f"[OK] Updated Official Data: Lot={lot}, Size={size}")
            updated += 1
        else:
            # If EQ failed, try SME and vice versa as a fallback
            other_series = "SME" if series == "EQ" else "EQ"
            print(f"   Retrying with {other_series}...")
            lot, size = fetch_official_details(symbol, other_series)
            if lot or size:
                update_data = {
                    "official_lot_size": lot,
                    "official_issue_size": size,
                    "issue_size": size, 
                    "lot_size": lot,    
                    "official_fetched_at": datetime.utcnow()
                }
                coll.update_one({"symbol": symbol}, {"$set": update_data})
                print(f"   [OK] Updated (Fallback {other_series}): Lot={lot}, Size={size}")
                updated += 1
            else:
                print(f"   [FAIL] No official data found for {symbol}")
                coll.update_one({"symbol": symbol}, {"$set": {"official_fetched_at": datetime.utcnow(), "official_fetch_failed": True}})
                failed += 1
            
        if count % 10 == 0:
            print(f"-- PROGRESS: {count}/{total_to_process} processed, {updated} updated, {failed} failed --")
            
        time.sleep(0.5) 

    print(f"\n>>> MASS UPDATE COMPLETE: {count} processed, {updated} updated, {failed} failed <<<")

if __name__ == "__main__":
    process_ipos()
