import csv
import time
import argparse
from pathlib import Path
from iposhala_test.scrapers.nse_company_dynamic import selenium_fetch_shareholding_pattern
from iposhala_test.scripts.mongo import ipo_past_master

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_CSV = DATA_DIR / "IPO_Past_Issues_main.m.csv"
VERIFIED_CSV = DATA_DIR / "verified_shareholding_patterns.csv"

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
                if clean_symbol not in unique_symbols:
                    targets.append(clean_symbol)
                    unique_symbols.add(clean_symbol)
    return targets

def parse_percentage(val):
    if not val:
        return 0.0
    try:
        return float(val)
    except:
        return 0.0

def main():
    parser = argparse.ArgumentParser(description="Fetch and save shareholding patterns to MongoDB.")
    parser.add_argument("--limit", type=int, help="Limit number of companies to process.")
    args = parser.parse_args()

    # Create verified CSV
    with open(VERIFIED_CSV, 'w', newline='', encoding='utf-8') as verified_file:
        fieldnames = ['Symbol', 'LatestDate', 'Promoter', 'Public']
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
                # 0. Check if data already exists in MongoDB
                existing_doc = ipo_past_master.find_one(
                    {"symbol": symbol, "nse_company.shareholding_patterns": {"$exists": True, "$not": {"$size": 0}}},
                    {"_id": 1}
                )
                
                if existing_doc:
                    print(f"  -> Data already exists in DB. Skipping fetch.")
                    count += 1
                    continue

                # 1. Fetch data
                result = selenium_fetch_shareholding_pattern(symbol)
                
                # Check if data is present and non-empty
                raw_data = result.get('data')
                
                if result.get('__available__') and raw_data and isinstance(raw_data, list) and len(raw_data) > 0:
                    
                    # 2. Parse Data
                    parsed_entries = []
                    for entry in raw_data:
                        # Extract relevant fields
                        # Keys identified from debug output: 'date', 'pr_and_prgrp', 'public_val', 'employeeTrusts', 'xbrl'
                        parsed_entry = {
                            "period": entry.get('date'), # e.g., "30-Sep-2024"
                            "promoter": parse_percentage(entry.get('pr_and_prgrp')),
                            "public": parse_percentage(entry.get('public_val')),
                            "employee_trusts": parse_percentage(entry.get('employeeTrusts')),
                            "source_url": entry.get('xbrl') or result.get('url'),
                            "submission_date": entry.get('submissionDate')
                        }
                        
                        # Filter out entries with no date or all zeros if desired (optional)
                        if parsed_entry['period']:
                             parsed_entries.append(parsed_entry)

                    # Sort by submission date or period? Period usually safer.
                    # Actually, the API usually returns sorted, but let's trust the order or just save as is.
                    
                    if parsed_entries:
                        # 3. Update MongoDB
                        update_result = ipo_past_master.update_one(
                            {"symbol": symbol},
                            {"$set": {"nse_company.shareholding_patterns": parsed_entries}}
                        )
                        
                        latest = parsed_entries[0] # Assuming first is latest or close to it
                        
                        if update_result.modified_count > 0:
                            print(f"  -> Updated MongoDB with {len(parsed_entries)} records.")
                            updated_count += 1
                        else:
                            print(f"  -> Data Exists (No DB Change).")
                        
                        # 4. Add to verified list
                        writer.writerow({
                            'Symbol': symbol, 
                            'LatestDate': latest.get('period'),
                            'Promoter': latest.get('promoter'),
                            'Public': latest.get('public')
                        })
                        verified_file.flush()
                        verified_count += 1
                    else:
                        print(f"  -> No valid entries parsed.")

                else:
                     print(f"  -> No data found (Code: {result.get('code')})")
                    
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
