from iposhala_test.scripts.mongo import ipo_past_master

def find_companies_with_financials():
    query = {"nse_company.financial_results": {"$type": "array", "$ne": []}}
    projection = {"symbol": 1, "nse_company.financial_results": 1}
    
    results = list(ipo_past_master.find(query, projection))
    
    if not results:
        print("No companies found with financial results.")
        return

    print(f"Found {len(results)} companies with financial results:")
    for doc in results:
        symbol = doc.get("symbol")
        financials = doc.get("nse_company", {}).get("financial_results", [])
        count = len(financials) if isinstance(financials, list) else 0
        print(f"- {symbol} ({count} periods)")

if __name__ == "__main__":
    find_companies_with_financials()
