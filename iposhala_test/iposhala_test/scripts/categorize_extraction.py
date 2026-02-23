
import json
from iposhala_test.scripts.mongo import ipo_past_master

def categorize():
    # Load successes
    try:
        with open('batch_5_financials.json', 'r') as f:
            successes = json.load(f)
    except:
        successes = {}
    
    success_symbols = set(successes.keys())
    
    # Fetch all targets
    all_docs = list(ipo_past_master.find({}, {"symbol": 1, "company_name": 1, "website": 1, "company_website": 1, "nse_quote.metadata.companyWebsite": 1}))
    
    category_map = {
        "success": [],
        "missing_website": [],
        "crawler_failure": []
    }
    
    for doc in all_docs:
        symbol = doc.get("symbol")
        name = doc.get("company_name", symbol)
        
        # Check website
        has_website = any([
            doc.get("website"),
            doc.get("company_website"),
            (doc.get("nse_quote") or {}).get("metadata", {}).get("companyWebsite")
        ])
        
        if symbol in success_symbols:
            category_map["success"].append(f"{name} ({symbol})")
        elif not has_website:
            category_map["missing_website"].append(f"{name} ({symbol})")
        else:
            category_map["crawler_failure"].append(f"{name} ({symbol})")
            
    # Print summary and first 15 for each
    for cat, items in category_map.items():
        print(f"\n--- {cat.upper()} ({len(items)}) ---")
        for item in items[:15]:
            print(f"- {item}")
        if len(items) > 15:
            print(f"... and {len(items)-15} more.")

    # Also save full lists to a file for reference
    with open('extraction_categories.json', 'w') as f:
        json.dump(category_map, f, indent=2)

if __name__ == "__main__":
    categorize()
