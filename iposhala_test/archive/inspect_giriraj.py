
import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def default_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()
    return str(o)

def inspect_giriraj():
    doc = ipo_past_master.find_one({"symbol": "GIRIRAJ"}, {"audited_financial_results": 1, "_id": 0})
    if doc:
        print(json.dumps(doc, indent=2, default=default_converter))
    else:
        print("GIRIRAJ not found")

if __name__ == "__main__":
    inspect_giriraj()
