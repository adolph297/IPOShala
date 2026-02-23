import sys
import os
import time
import requests
import json
from datetime import datetime
from pymongo import MongoClient, UpdateOne

# Add project root and inner iposhala_test to path for local imports
sys.path.append(os.path.join(os.getcwd(), "iposhala_test"))
from iposhala_test.scrapers.nse_company_dynamic import cookie_pool

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.nseindia.com",
}

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["iposhala"]
collection = db["ipo_past_master"]

def fetch_data(symbol):
    # Try equities first, then sme
    indexes = ["equities", "sme"]
    
    for index in indexes:
        url = f"https://www.nseindia.com/api/corporate-share-holdings-master?index={index}&symbol={symbol}"
        s = cookie_pool.get()
        try:
            r = s.get(url, headers=NSE_HEADERS, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0], url # Latest record
        except Exception as e:
            print(f"Error fetching {symbol} ({index}): {e}")
            pass
            
    return None, None

def run():
    print("🚀 Starting Shareholding Pattern Extraction...")
    
    # Get all symbols that don't have shareholding pattern or where it's empty
    # For now, let's just process ALL to be safe, or maybe filter
    cursor = collection.find({}, {"symbol": 1}).sort("listing_date", -1)
    symbols = [doc["symbol"] for doc in cursor if doc.get("symbol")]
    
    total = len(symbols)
    updated = 0
    skipped = 0
    
    ops = []
    
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{total}] Processing {symbol}...", end="", flush=True)
        
        data, source_url = fetch_data(symbol)
        
        if data:
            try:
                # Map fields
                promoter = float(data.get("pr_and_prgrp", 0) or 0)
                public = float(data.get("public_val", 0) or 0)
                trusts = float(data.get("employeeTrusts", 0) or 0)
                date = data.get("subMissnDate") or data.get("date")
                
                payload = {
                    "promoter": promoter,
                    "public": public,
                    "employee_trusts": trusts,
                    "date": date,
                    "source_url": source_url,
                    "raw_data": data # Keep raw just in case
                }
                
                ops.append(
                    UpdateOne(
                        {"symbol": symbol},
                        {"$set": {"nse_company.shareholding_pattern": payload}}
                    )
                )
                print(f" ✅ Found (P: {promoter}%)")
                updated += 1
            except Exception as e:
                print(f" ❌ Parse Error: {e}")
        else:
            print(" ⚠️  No Data")
            skipped += 1
            
        # Bulk write every 50
        if len(ops) >= 50:
            collection.bulk_write(ops)
            ops = []
            print("--- Saved Batch ---")
            
        time.sleep(0.5) # Rate limit
        
    if ops:
        collection.bulk_write(ops)
        print("--- Saved Final Batch ---")
        
    print(f"\n🎉 Complete! Updated: {updated}, Skipped: {skipped}")

if __name__ == "__main__":
    run()
