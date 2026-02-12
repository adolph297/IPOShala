
import os
import sys
from datetime import datetime, timezone
import time
from pymongo import MongoClient
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iposhala_test.scripts.mongo import ipo_past_master
from iposhala_test.scrapers.nse_company_dynamic import (
    fetch_announcements,
    fetch_annual_reports,
    fetch_brsr_reports,
    fetch_board_meetings,
    fetch_event_calendar,
    selenium_fetch_financial_results,
    selenium_fetch_shareholding_pattern
)

def populate_symbol(symbol):
    print(f">>> Populating data for {symbol} <<<")
    
    # 1. Fetch announcements
    print("Fetching announcements...")
    ann = fetch_announcements(symbol)
    items = ann.get("data") if ann.get("__available__") else []
    if isinstance(items, dict) and "data" in items: items = items["data"]
    if isinstance(items, list):
        items = [x for x in items if (x.get("symbol") or "").upper() == symbol]
    
    announcements = {
        "available": True if items else False,
        "payload": items,
        "source_url": ann.get("url")
    }
    print(f"  Got {len(items)} announcements.")

    # 2. Update DB
    update_payload = {
        "nse_company.announcements": announcements,
        "nse_company_updated_at": datetime.now(timezone.utc),
        "nse_company_fetched": True
    }
    
    # Try fetching financial results too
    try:
        print("Fetching financial results...")
        fr = selenium_fetch_financial_results(symbol)
        if fr.get("__available__"):
            update_payload["nse_company.financial_results"] = fr.get("data")
            print("  Financial results found.")
    except Exception as e:
        print(f"  Financial results fetch failed: {e}")

    result = ipo_past_master.update_one({"symbol": symbol}, {"$set": update_payload})
    if result.modified_count > 0:
        print(f"✅ Successfully updated {symbol} in ipo_past_master.")
    else:
        print(f"⚠️ No changes made to {symbol} (could be already matched or symbol not found).")

if __name__ == "__main__":
    populate_symbol("E2ERAIL")
