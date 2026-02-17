from iposhala_test.scripts.mongo import ipo_past_master
import json

def extract_websites():
    print("Extracting company websites from MongoDB (Exhaustive Search)...")
    
    # Check top fields we might have missed
    sample_doc = ipo_past_master.find_one({"symbol": "ADVANCE"})
    if sample_doc:
        print("\nFull Schema for 'ADVANCE' (Top level keys):")
        print(list(sample_doc.keys()))
        if "nse_quote" in sample_doc:
             print("nse_quote keys:", list(sample_doc["nse_quote"].keys()))
             if "info" in sample_doc["nse_quote"]:
                 print("nse_quote.info keys:", list(sample_doc["nse_quote"]["info"].keys()))

    target_symbols = ["ADVANCE", "AEGIS", "HDFCBANK", "RELIANCE", "TCS"]
    
    results = []
    
    # 1. Systematic check across multiple fields
    for symbol in target_symbols:
        doc = ipo_past_master.find_one({"symbol": symbol})
        if not doc: continue
        
        website = (
            doc.get("website") or 
            doc.get("company_website") or 
            doc.get("companyWebsite") or
            doc.get("nse_quote", {}).get("info", {}).get("companyWebsite") or
            doc.get("ipo_details", {}).get("website")
        )

        name = doc.get("company_name") or doc.get("nse_quote", {}).get("info", {}).get("companyName")
        results.append({
            "symbol": symbol,
            "company_name": name,
            "website": website
        })

    print(f"\nTarget Symbol Scan:")
    for res in results:
        print(f"- {res['symbol']} ({res['company_name']}): {res['website']}")

    # 2. Count those that HAVE a website in any of these fields
    query = {
        "$or": [
            {"website": {"$exists": True, "$ne": None}},
            {"company_website": {"$exists": True, "$ne": None}},
            {"companyWebsite": {"$exists": True, "$ne": None}},
            {"nse_quote.info.companyWebsite": {"$exists": True, "$ne": None}},
            {"ipo_details.website": {"$exists": True, "$ne": None}}
        ]
    }
    with_website = ipo_past_master.count_documents(query)
    total = ipo_past_master.count_documents({})
    print(f"\nOverall Statistics:")
    print(f"- Total Companies: {total}")
    print(f"- Companies with Website in DB: {with_website}")

    if with_website > 0:
        print("\nSample of companies with websites:")
        cursor = ipo_past_master.find(query, {"symbol": 1}).limit(5)
        for doc in cursor:
            print(f"- {doc['symbol']}")

if __name__ == "__main__":
    extract_websites()

if __name__ == "__main__":
    extract_websites()
