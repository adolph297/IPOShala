
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def update_manual_batch_3():
    updates = [
        {"symbol": "91ICFL29", "website": "https://www.indostarcapital.com/"},
        {"symbol": "75343PHF31", "website": "https://www.pnbhousing.com/"},
        {"symbol": "VICTORYEV", "website": "https://www.victoryevindia.com/"},
        {"symbol": "AELNCD3", "website": "https://www.adanienterprises.com/"},
        {"symbol": "E2ERAIL", "website": "https://etoerail.com/"},
        {"symbol": "DHARARAIL", "website": "https://drppl.com/"},
        {"symbol": "GKSL", "website": "https://www.gujaratsuperspecialityhospital.com/"},
        {"symbol": "EPWINDIA", "website": "https://epwindia.com/"},
        {"symbol": "SOCL", "website": "https://sundrex.co/"},
        {"symbol": "SHYAMDHANI", "website": "https://shyamspices.co.in/"},
        {"symbol": "MARC", "website": "http://www.mtplonline.in/"},
        {"symbol": "KSHINTL", "website": "https://www.kshinternational.com/"},
        {"symbol": "ICICIAMC", "website": "https://www.icicipruamc.com/"},
        {"symbol": "EXIMROUTES", "website": "https://eximroutes.ai/"},
        {"symbol": "ASHWINI", "website": "https://www.ashwinimovers.com/"}
    ]

    print(f"Updating {len(updates)} symbols...")
    for up in updates:
        symbol = up["symbol"]
        website = up["website"]
        res = ipo_past_master.update_many(
            {"symbol": symbol},
            {"$set": {"website": website, "website_source": "manual_search_batch_3"}}
        )
        print(f"Updated {symbol} -> {website} (Modified: {res.modified_count})")

if __name__ == "__main__":
    update_manual_batch_3()
