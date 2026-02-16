import csv
import time
import argparse
from pathlib import Path
from iposhala_test.scrapers.nse_company_dynamic import selenium_fetch_financial_results
from iposhala_test.scripts.mongo import ipo_past_master

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_CSV = DATA_DIR / "IPO_Past_Issues_main.m.csv"
VERIFIED_CSV = DATA_DIR / "verified_financial_results.csv"

def load_targets():
    """Load all companies from the main IPO list."""
    targets = []
    if not INPUT_CSV.exists():
        print(f"Error: Input CSV not found at {INPUT_CSV}")
        return []
    
    unique_symbols = set()
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row.get('Symbol')
            if symbol and symbol.strip():
                clean_symbol = symbol.strip()
                # Skip numeric or invalid symbols if any
                if clean_symbol not in unique_symbols:
                    targets.append(clean_symbol)
                    unique_symbols.add(clean_symbol)
    return targets

def main():
    parser = argparse.ArgumentParser(description="Fetch and save financial results to MongoDB.")
    parser.add_argument("--limit", type=int, help="Limit number of companies to process.")
    args = parser.parse_args()

    # Create verified CSV
    with open(VERIFIED_CSV, 'w', newline='', encoding='utf-8') as verified_file:
        fieldnames = ['Symbol', 'Count']
        writer = csv.DictWriter(verified_file, fieldnames=fieldnames)
        writer.writeheader()
        
        targets = load_targets()
        print(f"Loaded {len(targets)} candidates from availability list.")

        count = 0
        updated_count = 0
        verified_count = 0
        
        for symbol in targets:
            if args.limit and count >= args.limit:
                print(f"Limit of {args.limit} reached.")
                break
            
            print(f"[{count+1}/{len(targets)}] Processing {symbol}...")
            
            try:
                # 1. Fetch data
                result = selenium_fetch_financial_results(symbol)
                
                # Check if data is present and non-empty
                data = result.get('data')
                if result.get('__available__') and data and isinstance(data, (list, dict)) and len(data) > 0:
                    
                    # 2. Update MongoDB
                    update_result = ipo_past_master.update_one(
                        {"symbol": symbol},
                        {"$set": {"nse_company.financial_results": data}}
                    )
                    
                    if update_result.modified_count > 0:
                        print(f"  -> Updated MongoDB (Modified).")
                        updated_count += 1
                    else:
                        print(f"  -> Data Exists (No DB Change).")
                    
                    # 3. Add to verified list
                    writer.writerow({'Symbol': symbol, 'Count': len(data) if isinstance(data, list) else 1})
                    verified_file.flush()
                    verified_count += 1
                else:
                     print(f"  -> No data found (Index checked: {result.get('url')})")
                    
            except Exception as e:
                print(f"  -> Error: {e}")
                
            count += 1
            # Rate limiting
            time.sleep(1)

        print(f"\nDone. Processed {count} companies.")
        print(f"Verified & Saved: {verified_count}")
        print(f"DB Updates: {updated_count}")

if __name__ == "__main__":
    main()
