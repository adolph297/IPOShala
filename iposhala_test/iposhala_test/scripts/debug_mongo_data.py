from iposhala_test.scripts.mongo import ipo_past_master
import json
from bson import json_util

def debug_sampoorna():
    doc = ipo_past_master.find_one({"symbol": "SAMPOORNA"})
    if doc:
        financials = doc.get("nse_company", {}).get("financial_results")
        print(f"Type: {type(financials)}")
        print(f"Content: {json.dumps(financials, default=json_util.default, indent=2)}")
    else:
        print("SAMPOORNA not found")

if __name__ == "__main__":
    debug_sampoorna()
