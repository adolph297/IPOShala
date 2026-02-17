from iposhala_test.scripts.mongo import ipo_past_master
import json

def check_advance():
    print("=== Checking ADVANCE ===")
    doc = ipo_past_master.find_one({"symbol": "ADVANCE"})
    if not doc:
        print("ADVANCE not found in MongoDB.")
        # Try search case-insensitive or partial
        doc = ipo_past_master.find_one({"symbol": {"$regex": "^ADVANCE", "$options": "i"}})
        if doc:
            print(f"Found partial match: {doc.get('symbol')}")
    
    if doc:
        print(f"Symbol: {doc.get('symbol')}")
        print(f"performance_table length: {len(doc.get('performance_table', []))}")
        print(f"nse_historical keys: {list(doc.get('nse_historical', {}).keys())}")
        if doc.get("nse_historical", {}).get("rows"):
            print(f"nse_historical.rows length: {len(doc['nse_historical']['rows'])}")

def find_with_historical():
    print("\n=== Searching for any company with performance_table ===")
    query = {"performance_table": {"$exists": True, "$not": {"$size": 0}}}
    doc = ipo_past_master.find_one(query)
    if doc:
        print(f"Found {doc.get('symbol')} with performance_table ({len(doc['performance_table'])} rows)")
    else:
        print("No companies found with performance_table.")

    print("\n=== Searching for any company with nse_historical.rows ===")
    query2 = {"nse_historical.rows": {"$exists": True, "$not": {"$size": 0}}}
    doc2 = ipo_past_master.find_one(query2)
    if doc2:
        print(f"Found {doc2.get('symbol')} with nse_historical.rows ({len(doc2['nse_historical']['rows'])} rows)")
    else:
        print("No companies found with nse_historical.rows.")

if __name__ == "__main__":
    check_advance()
    find_with_historical()
