
from mongo import ipo_past_master
import pprint

symbol = "E2ERAIL"
print(f">>> Inspecting nse_company payloads for {symbol} <<<")

doc = ipo_past_master.find_one({"symbol": symbol}, {"nse_company": 1, "_id": 0})
if doc:
    nse_company = doc.get("nse_company")
    if nse_company:
        for key in ['announcements', 'corporate_actions']:
            if key in nse_company:
                print(f"\n--- {key} payload snippet ---")
                payload = nse_company[key].get('payload')
                if payload and isinstance(payload, list):
                    print(f"Count: {len(payload)}")
                    if len(payload) > 0:
                        pprint.pprint(payload[0])
                else:
                    print(f"Payload not found or not a list: {type(payload)}")
    else:
        print("nse_company is empty.")
else:
    print(f"No document found for {symbol}.")
