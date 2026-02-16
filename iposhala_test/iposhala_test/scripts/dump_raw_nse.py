from iposhala_test.scripts.mongo import ipo_past_master
import json

def dump_data():
    symbol = 'ADVANCE'
    doc = ipo_past_master.find_one({'symbol': symbol})
    if not doc:
        print("No doc found")
        return
    
    nse = doc.get('nse_company', {})
    with open('debug_nse_dump.json', 'w') as f:
        json.dump(nse, f, indent=2, default=str)
    print("Dumped to debug_nse_dump.json")

if __name__ == "__main__":
    dump_data()
