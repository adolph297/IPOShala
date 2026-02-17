from iposhala_test.scripts.mongo import ipo_past_master

def get_stats():
    total = ipo_past_master.count_documents({})
    
    # Check for audited_financials (website ingested)
    with_audited = ipo_past_master.count_documents({
        "nse_company.audited_financials": {"$exists": True, "$ne": []}
    })
    
    # Check for websites
    has_website = ipo_past_master.count_documents({
        "$or": [
            {"website": {"$exists": True, "$ne": None}},
            {"company_website": {"$exists": True, "$ne": None}},
            {"nse_quote.metadata.companyWebsite": {"$exists": True, "$ne": None}}
        ]
    })
    
    # Check for NSE native results (financial_results)
    with_nse_results = ipo_past_master.count_documents({
        "nse_company.financial_results.payload": {"$exists": True, "$ne": []}
    })

    print(f"Total Companies in DB: {total}")
    print(f"Companies with Website URL: {has_website}")
    print(f"Web Ingested (Audited Financials): {with_audited}")
    print(f"NSE Native Results Found: {with_nse_results}")

if __name__ == "__main__":
    get_stats()
