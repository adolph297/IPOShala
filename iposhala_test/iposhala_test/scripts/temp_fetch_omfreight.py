import yfinance as yf
from pymongo import MongoClient
from datetime import datetime
import json

def fetch_omfreight():
    symbol = "OMFREIGHT-SM.NS" # SME usually uses -SM.NS
    print(f"Fetching data for {symbol}...")
    
    # Oct 08, 2025 listing
    start_date = "2025-10-01"
    
    df = yf.download(symbol, start=start_date, progress=False)
    if df.empty:
        symbol = "OMFREIGHT.NS"
        print(f"Empty, trying {symbol}...")
        df = yf.download(symbol, start=start_date, progress=False)
    
    if df.empty:
        print("No data found on Yahoo Finance.")
        return

    df = df.reset_index()
    # Normalize column names to lowercase
    df.columns = [str(c[0] if isinstance(c, tuple) else c).lower() for c in df.columns]
    
    date_col = 'date'
    if 'date' not in df.columns:
        # Check if first column is date-like
        print(f"Columns found: {list(df.columns)}")
        if len(df.columns) > 0:
            date_col = df.columns[0]
    
    # Standardize
    rows = []
    for _, row in df.iterrows():
        dt = row[date_col]
        if hasattr(dt, 'to_pydatetime'):
            dt = dt.to_pydatetime()
        
        rows.append({
            "date": dt.strftime('%Y-%m-%d'),
            "open": float(row['open']),
            "high": float(row['high']),
            "low": float(row['low']),
            "close": float(row['close']),
            "volume": int(row['volume'])
        })
    
    print(f"Found {len(rows)} rows.")
    
    # Update Mongo
    client = MongoClient("mongodb://localhost:27017/")
    db = client["iposhala"]
    ipo_past_master = db["ipo_past_master"]
    
    res = ipo_past_master.update_one(
        {"symbol": "OMFREIGHT"},
        {"$set": {
            "performance_table": rows,
            "performance_updated_at": datetime.utcnow()
        }}
    )
    
    if res.modified_count > 0:
        print("Updated OMFREIGHT performance_table successfully.")
    else:
        print("No changes made to OMFREIGHT (maybe already up to date or not found).")

if __name__ == "__main__":
    fetch_omfreight()
