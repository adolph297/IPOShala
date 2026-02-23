
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def check_status():
    total_docs = ipo_past_master.count_documents({})
    
    # 1. Financials Coverage
    # Companies that have at least one audited financial report
    financials_query = {
        "nse_company.audited_financials": {"$exists": True, "$not": {"$size": 0}}
    }
    covered_financials = ipo_past_master.count_documents(financials_query)
    
    # 2. Website Coverage
    # Companies that have a website (eligible for extraction)
    website_query = {
        "$or": [
            {"website": {"$exists": True, "$ne": ""}},
            {"company_website": {"$exists": True, "$ne": ""}},
            {"nse_quote.metadata.companyWebsite": {"$exists": True, "$ne": ""}}
        ]
    }
    covered_websites = ipo_past_master.count_documents(website_query)
    
    # 3. Missing Websites (Blockers)
    missing_websites = total_docs - covered_websites

    print(f"--- Status Report ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    print(f"Total Companies: {total_docs}")
    print(f"Companies with Audited Financials extracted: {covered_financials} ({covered_financials/total_docs*100:.1f}%)")
    print(f"Companies with Website Available (Ready to Scan): {covered_websites} ({covered_websites/total_docs*100:.1f}%)")
    print(f"Companies MISSING Website (Discovery Needed): {missing_websites}")
    print("---------------------------------------------------")

if __name__ == "__main__":
    check_status()
