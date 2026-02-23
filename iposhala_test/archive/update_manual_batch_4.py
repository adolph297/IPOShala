
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def update_manual_batch_4():
    updates = [
        {"symbol": "PARKHOSPS", "website": "https://www.parkhospital.in/"},
        {"symbol": "NEPHROPLUS", "website": "https://www.nephroplus.com/"},
        {"symbol": "WAKEFIT", "website": "https://www.wakefit.co/"},
        {"symbol": "CORONA", "website": "https://www.coronaremedies.com/"},
        {"symbol": "ENCOMPAS", "website": "https://encompassmarkets.in/"},
        {"symbol": "FWSTC", "website": "https://www.fwstc.in/"},
        {"symbol": "VIDYAWIRES", "website": "https://vidyawire.com/"},
        {"symbol": "AEQUS", "website": "https://aequs.com/"},
        {"symbol": "MEESHO", "website": "https://meesho.com/"},
        {"symbol": "SHRIKANHA", "website": "http://www.kanhastainless.com/"},
        {"symbol": "NEOCHEM", "website": "https://neochem.in/"},
        {"symbol": "CSSL", "website": "https://www.cssindia.in/"},
        {"symbol": "SPEB", "website": "https://speb7.com/"},
        {"symbol": "INVICTA", "website": "https://pcdiagnostics.in/"},
        {"symbol": "SUDEEPPHRM", "website": "https://www.sudeeppharma.com/"}
    ]

    print(f"Updating {len(updates)} symbols...")
    for up in updates:
        symbol = up["symbol"]
        website = up["website"]
        res = ipo_past_master.update_many(
            {"symbol": symbol},
            {"$set": {"website": website, "website_source": "manual_search_batch_4"}}
        )
        print(f"Updated {symbol} -> {website} (Modified: {res.modified_count})")

if __name__ == "__main__":
    update_manual_batch_4()
