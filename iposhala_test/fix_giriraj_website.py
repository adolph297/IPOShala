
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def fix_websites():
    print("Starting website fix...")
    
    # GIRIRAJ
    print("Fixing GIRIRAJ...")
    res = ipo_past_master.update_one(
        {"symbol": "GIRIRAJ"}, 
        {"$set": {"website": "http://giriraj.co/", "website_source": "manual_fix_v2"}}
    )
    print(f"GIRIRAJ update acknowledged: {res.acknowledged}, Modified: {res.modified_count}, Matched: {res.matched_count}")
    
    doc = ipo_past_master.find_one({"symbol": "GIRIRAJ"}, {"website": 1})
    print(f"Verified GIRIRAJ website: {doc.get('website')}")

    # SABAR
    print("Fixing SABAR...")
    res = ipo_past_master.update_one(
        {"symbol": "SABAR"}, 
        {"$set": {"website": "http://sabarflex.com/", "website_source": "manual_fix_v2"}}
    )
    print(f"SABAR update acknowledged: {res.acknowledged}, Modified: {res.modified_count}, Matched: {res.matched_count}")

    doc = ipo_past_master.find_one({"symbol": "SABAR"}, {"website": 1})
    print(f"Verified SABAR website: {doc.get('website')}")

if __name__ == "__main__":
    fix_websites()
