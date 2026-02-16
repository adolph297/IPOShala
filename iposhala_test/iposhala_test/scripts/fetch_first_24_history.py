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
            nse_start = None
            nse_end = None
            
            if base_dt:
                nse_start = (base_dt - timedelta(days=5)).strftime('%d-%m-%Y')
                # Try to get 150 days of data or up to today
                end_dt = base_dt + timedelta(days=150)
                if end_dt > datetime.now():
                    end_dt = datetime.now()
                nse_end = end_dt.strftime('%d-%m-%Y')
            else:
                nse_start = (datetime.now() - timedelta(days=90)).strftime('%d-%m-%Y')
                nse_end = datetime.now().strftime('%d-%m-%Y')

            print(f" (nselib {nse_start} to {nse_end})...", end="", flush=True)
            try:
                df_nse = capital_market.price_volume_data(symbol, nse_start, nse_end)
            except Exception as e:
                # print(f" [nselib fetch err: {e}]", end="")
                df_nse = None
            
            if df_nse is not None and not df_nse.empty:
                # Map NSE columns to standardized names
                df_nse = df_nse.rename(columns={
                    'Date': 'date',
                    'OpenPrice': 'open',
                    'HighPrice': 'high',
                    'LowPrice': 'low',
                    'ClosePrice': 'close',
                    'TotalTradedQuantity': 'volume',
                     # Nselib sometimes returns different cases or column names
                    'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low', 'CLOSE': 'close', 'VOLUME': 'volume' 
                })
                
                # Check required columns
                required_cols = ['date', 'close']
                if all(col in df_nse.columns for col in required_cols):
                    # Clean numeric columns (NSE often returns strings with commas)
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        if col in df_nse.columns:
                             # Handle potential string issues
                            df_nse[col] = pd.to_numeric(
                                df_nse[col].astype(str).str.replace(',', '', regex=False), 
                                errors='coerce'
                            )
                    
                    # Convert date to string for JSON/Mongo safety
                    df_nse['date'] = df_nse['date'].astype(str)
                    
                    # Filter out rows with NaN dates/prices if any
                    df_nse = df_nse.dropna(subset=['date', 'close'])
                    
                    print(f" [Found {len(df_nse)} recs]", end="")
                    return df_nse.to_dict(orient="records")
        except Exception as e:
            print(f" [nselib outer err: {e}]", end="")
            # pass

    # 2. YAHOO FINANCE FALLBACK
    print(" (yf)...", end="", flush=True)
    # Define window for Yahoo
    if base_dt:
        yf_start = (base_dt - timedelta(days=5)).strftime('%Y-%m-%d') # slightly before listing
        end_dt = base_dt + timedelta(days=150)
        if end_dt > datetime.now():
            end_dt = datetime.now()
        yf_end = end_dt.strftime('%Y-%m-%d')
    else:
        yf_start = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        yf_end = datetime.now().strftime('%Y-%m-%d')

    found_data = False
    for suffix in [".NS", "-SM.NS", "-ST.NS", ".BO"]:
        yf_symbol = f"{symbol}{suffix}"
        try:
            # print(f" [try {yf_symbol}]", end="")
            df = yf.download(yf_symbol, start=yf_start, end=yf_end, progress=False, threads=False)
            if df is not None and not df.empty:
                df = df.reset_index()
                
                # Handling MultiIndex columns from newer yfinance versions
                if isinstance(df.columns, pd.MultiIndex):
                     # Flatten: use the top level name which is usually Price, Date
                     # Actually yf returns (Price, Ticker)
                     # We want Price.
                     # But commonly it is Date index, and columns are Open, High...
                     # If updated yf, columns might be (Adj Close, AAPL), (Close, AAPL)...
                     df.columns = [col[0] for col in df.columns.values]
                
                df.columns = [str(c).lower() for c in df.columns]

                # Standardize yf columns
                # yf usually uses 'date', 'open', 'high', etc.
                if 'date' in df.columns and 'close' in df.columns:
                    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                     
                    records = df.to_dict(orient="records")
                    if records:
                         print(f" [Found {len(records)} recs]", end="")
                         return records
        except Exception as e:
            # print(f"[yf err {suffix}: {e}]", end="")
            continue

    return []

def run_ingestion():
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return
        
    print(f"Reading CSV from: {CSV_PATH}")
    
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        
        # TARGET: First 24 IPOs from the CSV
        target_count = 24
        processed_count = 0
        
        print(f"Targeting first {target_count} IPOs from top of CSV...")
       
        for i, row in enumerate(reader, 1):
            if processed_count >= target_count:
                print(f"\nReached target of {target_count} IPOs. Stopping.")
                break

            symbol = row.get("Symbol", "").strip() or row.get("symbol", "").strip()
            if not symbol: continue
            
            # Listing date logic
            listing_date = row.get("DATE OF LISTING", "").strip()
            if not listing_date or listing_date == "-":
                 # Try ISSUE END DATE as proxy? No, likely not listed yet.
                 # But we can try to fetch anyway if it's recent.
                 pass

            # Update processed count for symbols successfully identified to be processed
            processed_count += 1
            
            print(f"\n[{processed_count}/{target_count}] Processing {symbol} (Listing: {listing_date})...", end="", flush=True)
            
            # Fetch data (Force fetch, ignoring existing to ensure update)
            try:
                perf_data = get_performance_data(symbol, listing_date)
            except Exception as e:
                print(f" [Error in get_performance_data: {e}]", end="")
                perf_data = []
            
            if perf_data:
                # Prepare update payload
                update_doc = {
                    "performance_table": perf_data, 
                    "performance_updated_at": datetime.now(timezone.utc)
                }
                
                # Only update company name if present
                c_name = row.get("COMPANY NAME") or row.get("Company Name")
                if c_name:
                    update_doc["company_name"] = c_name
                    
                if listing_date:
                    update_doc["listing_date_csv"] = listing_date
                
                ipo_past_master.update_one(
                    {"symbol": symbol},
                    {"$set": update_doc},
                    upsert=True
                )
                print(f" ✅ UPDATED DB", end="")
            else:
                print(" ❌ NO DATA FOUND", end="")
            
            time.sleep(1.0) # Rate limiting

if __name__ == "__main__":
    run_ingestion()
