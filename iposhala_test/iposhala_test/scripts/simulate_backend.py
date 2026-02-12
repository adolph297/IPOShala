
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Path setup to match backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iposhala_test.scripts.mongo import ipo_past_master
from iposhala_test.api.routes.company import fetch, unwrap_section

def simulate_api_call(symbol):
    print(f">>> SIMULATING API FOR {symbol} <<<")
    try:
        doc = fetch(symbol, {
            "symbol": 1,
            "company_name": 1,
            "security_type": 1,
            "nse_company.announcements": 1,
        })
        
        nse_company = doc.get("nse_company") or {}
        ann_raw = nse_company.get("announcements")
        ann_list = unwrap_section(ann_raw)
        
        print(f"Symbol: {doc.get('symbol')}")
        print(f"Announcements Raw Type: {type(ann_raw)}")
        print(f"Announcements Unwrapped Count: {len(ann_list)}")
        
        if len(ann_list) > 0:
            print("Successfully found data using backend logic!")
        else:
            print("Backend logic returned 0 even though DB has data. Investigation needed.")
            print(f"Raw Ann: {ann_raw}")
            
    except Exception as e:
        print(f"Simulation failed: {e}")

if __name__ == "__main__":
    simulate_api_call("E2ERAIL")
