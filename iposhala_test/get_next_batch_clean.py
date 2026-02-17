
import os
import sys
import json

# Add project root to path
sys.path.append(os.getcwd())

# Suppress stdout/stderr for import
original_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
from iposhala_test.scripts.mongo import ipo_past_master
sys.stdout = original_stdout

def get_next_batch_json(limit):
    # Find documents where 'website' does not exist
    query = {"website": {"$exists": False}}
    cursor = ipo_past_master.find(query, {"symbol": 1, "company_name": 1, "_id": 0}).limit(limit)
    
    results = []
    seen_symbols = set()
    
    for doc in cursor:
        symbol = doc.get("symbol")
        if symbol and symbol not in seen_symbols:
            results.append({
                "symbol": symbol,
                "name": doc.get("company_name", symbol)
            })
            seen_symbols.add(symbol)
            
    with open("batch_next.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Wrote {len(results)} items to batch_next.json")

if __name__ == "__main__":
    try:
        limit = int(sys.argv[1])
    except:
        limit = 20
    get_next_batch_json(limit)
