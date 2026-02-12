
from mongo import ipo_master
import pprint

symbol = "E2ERAIL"
print(f">>> Inspecting ipo_master for {symbol} <<<")

doc = ipo_master.find_one({"symbol": symbol})
if doc:
    pprint.pprint(doc)
else:
    print(f"No document found for {symbol} in ipo_master. Checking first 5 documents...")
    for d in ipo_master.find().limit(5):
        print(f"\n- Symbol: {d.get('symbol')}")
        pprint.pprint(d)
