
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def update_manual_batch():
    updates = [
        {"symbol": "SAMPOORNA", "website": "http://sampoornanuts.com/"},
        {"symbol": "GJL", "website": "http://groverjewells.com/"},
        {"symbol": "BRANDMAN", "website": "http://brandmanretail.com/"},
        {"symbol": "KRMAYURVED", "website": "http://krmayurvedaindia.com/"},
        {"symbol": "SHADOWFAX", "website": "https://www.shadowfax.in/"},
        {"symbol": "PFC2026", "website": "https://pfcindia.com/"},
        {"symbol": "PFCZCB1", "website": "https://pfcindia.com/"},
        {"symbol": "ARMOUR", "website": "http://www.armoursecurities.com/"},
        {"symbol": "AMAGI", "website": "https://amagi.com/"},
        {"symbol": "AVANA", "website": "http://avanaelectrosystems.com/"},
        {"symbol": "BHARATCOAL", "website": "http://bcclweb.in/"}
    ]

    print(f"Updating {len(updates)} companies...")
    for up in updates:
        symbol = up["symbol"]
        website = up["website"]
        res = ipo_past_master.update_one(
            {"symbol": symbol},
            {"$set": {"website": website, "website_source": "manual_search_batch"}}
        )
        print(f"Updated {symbol} -> {website} (Ack: {res.acknowledged})")

if __name__ == "__main__":
    update_manual_batch()
