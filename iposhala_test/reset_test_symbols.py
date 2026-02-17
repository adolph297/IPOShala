
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def reset_symbols():
    symbols = ['BRANDMAN', 'PFC2026', 'PFCZCB1', 'SAMPOORNA', 'GJL']
    print(f"Resetting website for {symbols}...")
    
    res = ipo_past_master.update_many(
        {"symbol": {"$in": symbols}},
        {"$unset": {"website": "", "website_source": ""}}
    )
    print(f"Reset complete. Modified: {res.modified_count}")

if __name__ == "__main__":
    reset_symbols()
