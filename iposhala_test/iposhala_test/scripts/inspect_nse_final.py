
from mongo import ipo_past_master
import pprint

symbol = "E2ERAIL"
print(f">>> Final Inspection of nse_company for {symbol} <<<")

doc = ipo_past_master.find_one({"symbol": symbol}, {"nse_company": 1, "_id": 0})
if doc:
    nse_company = doc.get("nse_company")
    if nse_company:
        for key, val in nse_company.items():
            print(f"\n--- {key} ({type(val)}) ---")
            if isinstance(val, dict):
                print(f"Keys: {list(val.keys())}")
                if 'payload' in val:
                    payload = val['payload']
                    if isinstance(payload, list):
                        print(f"Payload Count: {len(payload)}")
                        if len(payload) > 0:
                            pprint.pprint(payload[0])
                    else:
                        print(f"Payload (not a list): {payload}")
                else:
                    pprint.pprint(val)
            elif isinstance(val, list):
                print(f"Item Count: {len(val)}")
                if len(val) > 0:
                    pprint.pprint(val[0])
            else:
                print(f"Value: {val}")
    else:
        print("nse_company is empty.")
else:
    print(f"No document found for {symbol}.")
