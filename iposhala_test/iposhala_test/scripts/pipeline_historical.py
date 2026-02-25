import os
import sys
import time
import argparse
import logging
from datetime import datetime, timezone, timedelta
import yfinance as yf
import pandas as pd

# Add project root to path
sys.path.append(os.getcwd())
try:
    from iposhala_test.scripts.mongo import ipo_past_master
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_yfinance_historical(symbol, period="2y"):
    """
    Fetch historical performance table direct from Yahoo Finance APIs.
    We iterate over standard suffixes for NSE and BSE.
    """
    for suffix in [".NS", "-SM.NS", "-ST.NS", ".BO"]:
        yf_sym = f"{symbol}{suffix}"
        try:
            df = yf.download(yf_sym, period=period, progress=False, threads=False)
            if df is not None and not df.empty:
                df = df.reset_index()
                
                # Flatten multi-index if necessary
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [c[0] if c[1] == "" else c[0] for c in df.columns]
                
                df.columns = [str(c).lower() for c in df.columns]
                
                perf_data = []
                for _, row in df.iterrows():
                    perf_data.append({
                        "date": row["date"].strftime("%Y-%m-%d") if hasattr(row["date"], "strftime") else str(row["date"]),
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": int(row["volume"]) if "volume" in row and not pd.isna(row["volume"]) else 0
                    })
                
                # Sort descending to align with frontend tables natively
                perf_data.sort(key=lambda x: x["date"], reverse=True)
                return perf_data
        except:
            continue
    return []

def run_historical_pipeline(limit=None, symbols=None, force=False):
    """
    Iterate over companies in MongoDB and attach full historical OHLCV profiles.
    """
    query = {"performance_table": {"$exists": False}} if not force else {}
    if symbols: query["symbol"] = {"$in": symbols}
    
    companies = list(ipo_past_master.find(query, {"symbol": 1}).limit(limit if limit else 0))
    logging.info(f"[HISTORICAL] Found {len(companies)} candidates for data extraction.")
    
    count = 0
    for idx, comp in enumerate(companies):
        sym = comp['symbol']
        logging.info(f"[{idx+1}/{len(companies)}] Fetching historical sequence for {sym}...")
        
        perf_data = fetch_yfinance_historical(sym)
        if perf_data:
            ipo_past_master.update_one(
                {"symbol": sym},
                {"$set": {
                    "performance_table": perf_data,
                    "performance_updated_at": datetime.now(timezone.utc)
                }}
            )
            logging.info(f"  [SUCCESS] -> Hydrated {len(perf_data)} daily records into MongoDB")
            count += 1
        else:
            logging.info(f"  [FAILED] -> No Yahoo Finance match located.")
            
        time.sleep(0.5)
        
    logging.info(f"Finished. Successfully extracted data for {count}/{len(companies)} companies.")

def main():
    parser = argparse.ArgumentParser(description="Unified Historical Data Extraction Pipeline")
    parser.add_argument("--limit", type=int, help="Limit maximum records to scan.")
    parser.add_argument("--symbols", nargs="+", help="Specific symbols to target.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing historical tables.")
    args = parser.parse_args()

    run_historical_pipeline(args.limit, args.symbols, args.force)

if __name__ == "__main__":
    main()
