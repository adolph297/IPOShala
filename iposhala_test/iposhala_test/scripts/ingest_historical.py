import yfinance as yf
import pandas as pd
from datetime import datetime, timezone
from iposhala_test.scripts.mongo import ipo_past_master

def ingest_historical(symbol):
    print(f"Ingesting historical data for {symbol}...")
    
    # Try NSE first, then BSE
    for suffix in [".NS", ".BO"]:
        yf_sym = f"{symbol}{suffix}"
        print(f"Fetching from {yf_sym}...")
        try:
            # Fetch last 2 years of data (should be enough for most IPOs)
            df = yf.download(yf_sym, period="2y", progress=False)
            if not df.empty:
                # Prepare data for MongoDB
                # yfinance returns multi-index if multiple symbols, but here it's single
                df = df.reset_index()
                
                # Flatten columns if multi-indexed
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [c[0] if c[1] == "" else c[0] for c in df.columns]

                df.columns = [str(c).lower() for c in df.columns]
                
                # Rename columns to match performance_table schema
                # Current yfinance columns usually: date, open, high, low, close, adj close, volume
                # Our schema: open, close, high, low, date
                
                perf_data = []
                for _, row in df.iterrows():
                    perf_data.append({
                        "date": row["date"].strftime("%Y-%m-%d") if hasattr(row["date"], "strftime") else str(row["date"]),
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": int(row["volume"]) if "volume" in row else 0
                    })
                
                # Sort by date descending (optional, frontend handles it but good for consistency)
                perf_data.sort(key=lambda x: x["date"], reverse=True)

                # Update MongoDB
                res = ipo_past_master.update_one(
                    {"symbol": symbol},
                    {
                        "$set": {
                            "performance_table": perf_data,
                            "last_ingested_historical": datetime.now(timezone.utc)
                        }
                    }
                )
                print(f"✅ Successfully ingested {len(perf_data)} rows for {symbol}. (Matched: {res.matched_count}, Modified: {res.modified_count})")
                return True
        except Exception as e:
            print(f"❌ Error fetching from {yf_sym}: {e}")
            
    print(f"⚠️ No data found for {symbol} on Yahoo Finance.")
    return False

if __name__ == "__main__":
    import sys
    sym = sys.argv[1] if len(sys.argv) > 1 else "ADVANCE"
    ingest_historical(sym)
