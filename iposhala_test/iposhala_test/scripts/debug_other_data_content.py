from iposhala_test.scripts.mongo import ipo_past_master
import json
from bson import json_util

def debug_content():
    symbol = "SAMPOORNA"
    doc = ipo_past_master.find_one({"symbol": symbol})
    
    if not doc:
        print(f"{symbol} not found")
        return

    company = doc.get("nse_company", {})
    
    fields = ["corporate_actions", "board_meetings", "event_calendar"]
    
    for field in fields:
        data = company.get(field)
        print(f"\n--- {field} ---")
        print(f"Type: {type(data)}")
        if data:
            print(json.dumps(data, default=json_util.default, indent=2))
        else:
            print("Empty/None")

if __name__ == "__main__":
    debug_content()
