
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def fix_batch1():
    print("Starting batch 1 website fix...")
    
    updates = [
        {"symbol": "GLOBAL", "website": "http://globaledu.net.in/"},
        {"symbol": "MUKTI", "website": "http://mukti.net.in/"}, 
        {"symbol": "MAHALAXMI", "website": "http://mrtglobal.com/"},
        {"symbol": "SSOVERSEAS", "website": "http://ssoverseas.info/"} # Best guess
    ]

    for up in updates:
        symbol = up["symbol"]
        website = up["website"]
        print(f"Fixing {symbol} -> {website}...")
        res = ipo_past_master.update_one(
            {"symbol": symbol}, 
            {"$set": {"website": website, "website_source": "manual_fix_batch1"}}
        )
        print(f"{symbol} update acknowledged: {res.acknowledged}, Modified: {res.modified_count}, Matched: {res.matched_count}")
        
        doc = ipo_past_master.find_one({"symbol": symbol}, {"website": 1})
        print(f"Verified {symbol} website: {doc.get('website')}")

if __name__ == "__main__":
    fix_batch1()
