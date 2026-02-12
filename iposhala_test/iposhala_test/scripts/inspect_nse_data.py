
from mongo import ipo_past_master
import pprint

symbol = "E2ERAIL"
print(f">>> Inspecting nse_company for {symbol} <<<")

doc = ipo_past_master.find_one({"symbol": symbol}, {"nse_company": 1, "nse_quote": 1, "_id": 0})
if doc:
    nse_company = doc.get("nse_company")
    if nse_company:
        print("\n--- nse_company keys ---")
        pprint.pprint(list(nse_company.keys()))
        
        # Look for the specific areas
        for key in ['announcements', 'corporateActions', 'historicalData', 'annualReports', 'shareholdingPattern']:
            if key in nse_company:
                print(f"\n- Found {key} (type: {type(nse_company[key])})")
                val = nse_company[key]
                if isinstance(val, list):
                    print(f"  Count: {len(val)}")
                    if len(val) > 0:
                         pprint.pprint(val[0])
                elif isinstance(val, dict):
                    pprint.pprint(list(val.keys()))
    else:
        print("nse_company is empty or missing.")
        
    nse_quote = doc.get("nse_quote")
    if nse_quote:
        print("\n--- nse_quote keys ---")
        pprint.pprint(list(nse_quote.keys()))
else:
    print(f"No document found for {symbol} in ipo_past_master.")
