
import os
import sys
import time
import random
from duckduckgo_search import DDGS
from iposhala_test.scripts.mongo import ipo_past_master

# Add project root to path
sys.path.append(os.getcwd())

def clean_company_name(name):
    # Remove -Issue Withdrawn, (...), etc.
    name = name.split("-")[0]
    name = name.split("(")[0]
    return name.strip()

def search_website(company_name):
    """
    Search for 'Company Name official website' on DuckDuckGo.
    Returns the first organic result URL.
    """
    clean_name = clean_company_name(company_name)
    query = f"{clean_name} official website"
    print(f"    Query: {query}")
    
    excluded_domains = [
        "chittorgarh.com", "moneycontrol.com", "screener.in", "groww.in", 
        "economictimes.indiatimes.com", "investorgain.com", "ipowatch.in",
        "stockmarket.com", "bseindia.com", "nseindia.com", "zaubacorp.com",
        "tofler.in", "wikipedia.org", "youtube.com", "facebook.com",
        "linkedin.com", "instagram.com", "justdial.com", "indiamart.com",
        "glassdoor.co.in", "ambitionbox.com", "99acres.com", "magicbricks.com"
    ]

    try:
        with DDGS() as ddgs:
            # Fetch more results to filter locally
            # Use backend='lite' again as html was worse
            results = list(ddgs.text(query, max_results=10, backend='lite'))
            if results:
                for r in results:
                    href = r['href']
                    title = r['title']
                    
                    # Filter out aggregators
                    if any(ex in href for ex in excluded_domains):
                        continue
                    
                    # Basic domain match check
                    # e.g. "Brandman Retail" -> check if "brandman" in domain
                    # Very basic check: split name into words, check if at least one significant word is in domain
                    name_parts = [w.lower() for w in clean_name.split() if len(w) > 3 and w.lower() not in ["limited", "private", "ltd", "pvt", "india", "retail", "services", "solutions"]]
                    if not name_parts:
                        # If name has no significant parts (e.g. "ABC Ltd"), check whole name string
                        name_parts = [clean_name.lower().replace(" ", "")]
                    
                    domain = href.split("//")[-1].split("/")[0].lower()
                    
                    if any(part in domain for part in name_parts):
                        print(f"    Candidate (Matched): {href}")
                        return href
                    else:
                        print(f"    Skipping candidate (No fuzzy match): {href}")
                    
    except Exception as e:
        print(f"  Search error for {company_name}: {e}")
        return None
    return None

def mass_discovery(limit=10):
    """
    Find companies without websites and populate them using search.
    """
    query = {
        '$and': [
            {'website': {'$exists': False}}, 
            {'company_website': {'$exists': False}}, 
            {'nse_quote.metadata.companyWebsite': {'$exists': False}},
            # Exclude ones we just marked as manual fix if you want, 
            # but better to validte if 'website' field exists
        ]
    }
    
    # Get a batch
    cursor = ipo_past_master.find(query, {'symbol': 1, 'company_name': 1}).limit(limit)
    companies = list(cursor)
    
    if not companies:
        print("No companies found missing websites!")
        return

    print(f"Starting mass discovery for {len(companies)} companies...")

    for i, company in enumerate(companies):
        symbol = company.get('symbol')
        name = company.get('company_name')
        
        print(f"[{i+1}/{len(companies)}] Searching for: {name} ({symbol})")
        
        url = search_website(name)
        
        if url:
            print(f"  Found: {url}")
            # Update DB
            ipo_past_master.update_one(
                {"_id": company["_id"]},
                {"$set": {"website": url, "website_source": "ddg_mass_discovery"}}
            )
        else:
            print(f"  No URL found.")
        
        # Random sleep to avoid rate limits
        sleep_time = random.uniform(5, 10)
        time.sleep(sleep_time)

if __name__ == "__main__":
    # You can pass a limit arg if needed
    limit = 5
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except:
            pass
    mass_discovery(limit)
