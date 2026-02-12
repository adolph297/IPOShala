import csv
import os
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

try:
    from nselib import capital_market
except ImportError:
    print("Warning: nselib not found. Will use only Yahoo Finance.")
    capital_market = None

# --- DATABASE SETUP ---
try:
    from iposhala_test.scripts.mongo import ipo_past_master
except ImportError:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["iposhala"]
    ipo_past_master = db["ipo_past_master"]

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "IPO_Past_Issues_main.m.csv")

def get_performance_data(symbol, start_date_str):
    # Clean the symbol
    symbol = "".join(e for e in symbol if e.isalnum())
    
    base_dt = None
    if start_date_str and start_date_str != "-":
        for fmt in ["%d-%b-%Y", "%d-%m-%Y", "%Y-%m-%d"]:
            try:
                base_dt = datetime.strptime(start_date_str, fmt)
                break
            except:
                continue

    # 1. TRY NSELIB (Direct NSE Data - Reliable for SMEs)
    if capital_market:
        try:
            # If no listing date, try last 90 days as fallback
            if base_dt:
                nse_start = (base_dt - timedelta(days=5)).strftime('%d-%m-%Y')
                nse_end = (base_dt + timedelta(days=150)).strftime('%d-%m-%Y')
            else:
                nse_start = (datetime.now() - timedelta(days=90)).strftime('%d-%m-%Y')
                nse_end = datetime.now().strftime('%d-%m-%Y')

            print(f" (nselib {nse_start})...", end="", flush=True)
            df_nse = capital_market.price_volume_data(symbol, nse_start, nse_end)
            
            if df_nse is not None and not df_nse.empty:
                # Map NSE columns to standardized names
                df_nse = df_nse.rename(columns={
                    'Date': 'date',
                    'OpenPrice': 'open',
                    'HighPrice': 'high',
                    'LowPrice': 'low',
                    'ClosePrice': 'close',
                    'TotalTradedQuantity': 'volume'
                })
                # Clean numeric columns (NSE often returns strings with commas)
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    if col in df_nse.columns:
                        df_nse[col] = pd.to_numeric(df_nse[col].astype(str).str.replace(',', ''), errors='coerce')
                
                # Convert date to string for JSON/Mongo safety
                df_nse['date'] = df_nse['date'].astype(str)
                
                return df_nse.to_dict(orient="records")
        except Exception as e:
            # print(f"nselib error: {e}")
            pass

    # 2. YAHOO FINANCE FALLBACK
    print(" (yf)...", end="", flush=True)
    # Define window for Yahoo
    if base_dt:
        yf_start = (base_dt - timedelta(days=15)).strftime('%Y-%m-%d')
        yf_end = (base_dt + timedelta(days=150)).strftime('%Y-%m-%d')
    else:
        yf_start = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        yf_end = datetime.now().strftime('%Y-%m-%d')

    for suffix in [".NS", "-SM.NS", "-ST.NS", ".BO"]:
        yf_symbol = f"{symbol}{suffix}"
        try:
            df = yf.download(yf_symbol, start=yf_start, end=yf_end, progress=False, threads=False)
            if df is not None and not df.empty:
                df = df.reset_index()
                df.columns = [str(c).lower() for c in df.columns]
                # Standardize yf columns if needed (yf usually uses 'date', 'open', 'high', etc. already)
                # But ensure 'date' is string
                if 'date' in df.columns:
                    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                return df.to_dict(orient="records")
        except:
            continue

    return []

def run_ingestion():
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return
    
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        total = len(reader)
        
        # We can sort to process newest first (assuming recent ones are at the top)
        # or just go through them.
        for i, row in enumerate(reader, 1):
            symbol = row.get("Symbol", "").strip() or row.get("symbol", "").strip()
            if not symbol: continue
            
            # RESUME LOGIC: Only fetch if empty or missing
            existing = ipo_past_master.find_one({"symbol": symbol}, {"performance_table": 1})
            if existing and existing.get("performance_table") and len(existing["performance_table"]) > 0:
                continue

            print(f"🔄 [{i}/{total}] {symbol}...", end="", flush=True)
            perf_data = get_performance_data(symbol, row.get("DATE OF LISTING", ""))
            
            if perf_data:
                ipo_past_master.update_one(
                    {"symbol": symbol},
                    {"$set": {
                        "company_name": row.get("COMPANY NAME") or row.get("Company Name"),
                        "listing_date_csv": row.get("DATE OF LISTING"),
                        "performance_table": perf_data, 
                        "performance_updated_at": datetime.now(timezone.utc)
                    }},
                    upsert=True
                )
                print(f" ✅ FIXED ({len(perf_data)} rows)")
            else:
                print(" ❌ EMPTY")
            
            time.sleep(0.5) # Be kind to servers

if __name__ == "__main__":
    print("Starting Multi-Source Performance Ingestion...")
    print(f"Reading from: {CSV_PATH}")
    run_ingestion()
