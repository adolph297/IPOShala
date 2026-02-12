import csv
import os
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from nselib import capital_market

# --- DATABASE SETUP ---
client = MongoClient("mongodb://localhost:27017/")
db = client["iposhala"]
collection = db["ipo_past_master"]

def get_performance_data(symbol, start_date_str):
    if not start_date_str or start_date_str == "-": return []
    
    # Clean the symbol (Removes any hidden spaces or special characters)
    symbol = "".join(e for e in symbol if e.isalnum())
    
    try:
        base_dt = datetime.strptime(start_date_str, "%d-%b-%Y")
        
        # 1. YAHOO FINANCE - SEARCH BOTH NSE & BSE
        # We search a huge window (120 days) because old IPO data is often delayed
        for suffix in [".NS", ".BO"]:
            yf_symbol = f"{symbol}{suffix}"
            df = yf.download(yf_symbol, 
                             start=(base_dt - timedelta(days=15)).strftime('%Y-%m-%d'),
                             end=(base_dt + timedelta(days=120)).strftime('%Y-%m-%d'),
                             progress=False, threads=False)
            if not df.empty:
                df = df.reset_index()
                df.columns = [str(c).lower() for c in df.columns]
                return df.to_dict(orient="records")

        # 2. NSE OFFICIAL - MULTI-SERIES DEEP SCAN
        # This fixes THEJO, MITCON, VETO which are SME veterans
        nse_start = (base_dt - timedelta(days=10)).strftime('%d-%m-%Y')
        nse_end = (base_dt + timedelta(days=120)).strftime('%d-%m-%Y')
        
        for series in ["SM", "ST", "EQ", "BE"]:
            try:
                # Direct call to NSE India servers
                df_nse = capital_market.price_equity_historical(symbol, nse_start, nse_end, series=series)
                if df_nse is not None and not df_nse.empty:
                    df_nse.columns = [str(c).lower() for c in df_nse.columns]
                    df_nse = df_nse.rename(columns={
                        'open_price': 'open', 'close_price': 'close',
                        'high_price': 'high', 'low_price': 'low', 'price_date': 'date'
                    })
                    return df_nse.to_dict(orient="records")
            except:
                continue

    except Exception:
        pass
    return []

def run_ingestion():
    csv_path = r"C:\Users\Dell\Desktop\Rusaka-Technologies\Iposhala\iposhala_test\iposhala_test\data\IPO_Past_Issues_main.m.csv"
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        total = len(reader)
        
        for i, row in enumerate(reader, 1):
            symbol = row["Symbol"].strip()
            
            # RESUME LOGIC: Only skip if we actually have data
            existing = collection.find_one({"symbol": symbol})
            if existing and existing.get("performance_table") and len(existing["performance_table"]) > 0:
                continue

            print(f"🔄 [{i}/{total}] {symbol}...", end=" ", flush=True)
            perf_data = get_performance_data(symbol, row["DATE OF LISTING"])
            
            if perf_data:
                collection.update_one(
                    {"symbol": symbol},
                    {"$set": {
                        "company_name": row.get("Company Name", "").strip(),
                        "listing_date": row["DATE OF LISTING"],
                        "performance_table": perf_data, 
                        "updated_at": datetime.now(timezone.utc)
                    }},
                    upsert=True
                )
                print("✅ FIXED")
            else:
                print("❌ STILL EMPTY")
            
            # Small delay to prevent IP blocking from NSE
            time.sleep(0.6)

if __name__ == "__main__":
    print("Starting Deep-Scan Ingestion...")
    run_ingestion()