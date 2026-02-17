
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def update_manual_batch_2():
    # Batch 2: 5 unique companies covering 10 records
    updates = [
        {"symbol": "ADANIENPP1", "website": "https://www.adanienterprises.com/"},
        {"symbol": "14DCCL31A", "website": "http://darcredit.com/"},
        {"symbol": "1150AFIL29", "website": "http://akmefintrade.com/"},
        {"symbol": "783CIFCL28", "website": "https://www.cholamandalam.com/"},
        {"symbol": "1165ESFB32", "website": "https://www.esaf.bank/"}
    ]

    print(f"Updating {len(updates)} symbols (using update_many)...")
    for up in updates:
        symbol = up["symbol"]
        website = up["website"]
        res = ipo_past_master.update_many(
            {"symbol": symbol},
            {"$set": {"website": website, "website_source": "manual_search_batch_2"}}
        )
        print(f"Updated {symbol} -> {website} (Modified: {res.modified_count})")

if __name__ == "__main__":
    update_manual_batch_2()
