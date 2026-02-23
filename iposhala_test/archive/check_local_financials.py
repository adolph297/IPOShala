
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["iposhala"]
coll = db["ipo_past_master"]

# Check for any doc with financial results
doc = coll.find_one({
    "$or": [
        {"nse_company.financial_results.payload": {"$exists": True, "$not": {"$size": 0}}},
        {"nse_company.audited_financials": {"$exists": True, "$not": {"$size": 0}}}
    ]
})

if doc:
    print(f"Found sample with financials: {doc['symbol']}")
    fin = doc.get("nse_company", {}).get("financial_results", {}).get("payload", [])
    aud = doc.get("nse_company", {}).get("audited_financials", [])
    print(f"NSE Results count: {len(fin)}")
    print(f"Audited Results count: {len(aud)}")
else:
    print("No documents found with financial results in local DB.")
