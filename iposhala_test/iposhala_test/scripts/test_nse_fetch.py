"""
Quick test to verify NSE data fetching works
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iposhala_test.scrapers.nse_company_dynamic import fetch_announcements
from iposhala_test.scripts.mongo import ipo_past_master
from datetime import datetime, timezone

symbol = "RELIANCE"

print(f"Testing NSE data fetch for {symbol}...")

# Test fetch
print("Fetching announcements...")
result = fetch_announcements(symbol)

print(f"Available: {result.get('__available__')}")
print(f"URL: {result.get('url')}")

if result.get("__available__"):
    data = result.get("data", {})
    if isinstance(data, dict) and "data" in data:
        items = data.get("data", [])
    elif isinstance(data, list):
        items = data
    else:
        items = []
    
    print(f"Found {len(items)} total items")
    
    # Filter by symbol
    filtered = [x for x in items if (x.get("symbol", "") or "").upper() == symbol]
    print(f"Found {len(filtered)} items for {symbol}")
    
    if filtered:
        print("\nFirst announcement:")
        print(f"  Date: {filtered[0].get('an_dt')}")
        print(f"  Description: {filtered[0].get('desc', '')[:100]}")
        print(f"  Attachment: {filtered[0].get('attchmntFile', 'N/A')}")
    
    # Update MongoDB
    print(f"\nUpdating MongoDB...")
    wrapped = {
        "available": bool(filtered),
        "payload": filtered,
        "source_url": result.get("url")
    }
    
    update_result = ipo_past_master.update_one(
        {"symbol": symbol},
        {"$set": {
            "nse_company.announcements": wrapped,
            "nse_company_updated_at": datetime.now(timezone.utc)
        }}
    )
    
    print(f"Modified count: {update_result.modified_count}")
    print("✅ Test successful!")
else:
    print("❌ Data not available")
