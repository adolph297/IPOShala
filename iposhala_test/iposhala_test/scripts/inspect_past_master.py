
from mongo import ipo_past_master
import pprint

symbol = "E2ERAIL"
print(f">>> Inspecting ipo_past_master for {symbol} <<<")

doc = ipo_past_master.find_one({"symbol": symbol})
if doc:
    print(f"Found document for {symbol} in ipo_past_master.")
    # Print keys to see the structure without dumping potentially huge data
    print(f"Top-level keys: {list(doc.keys())}")
    
    # Check for specific keys the user might be referring to
    interesting_keys = ['announcements', 'historical_data', 'corporate_actions', 'annual_reports', 'shareholding_pattern']
    for key in interesting_keys:
        if key in doc:
            print(f"Found key: {key} (type: {type(doc[key])})")
            # Show a snippet
            snippet = doc[key]
            if isinstance(snippet, list):
                print(f"  Count: {len(snippet)}")
                if len(snippet) > 0:
                    pprint.pprint(snippet[0])
            else:
                pprint.pprint(snippet)

else:
    print(f"No document found for {symbol} in ipo_past_master.")
    # Check what symbols ARE there
    symbols = ipo_past_master.distinct("symbol")
    print(f"Total symbols in ipo_past_master: {len(symbols)}")
    print(f"First 10 symbols: {symbols[:10]}")
