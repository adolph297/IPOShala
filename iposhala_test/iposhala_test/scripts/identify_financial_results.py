import csv
import os
import time
import argparse
from pathlib import Path
from iposhala_test.scrapers.nse_company_dynamic import selenium_fetch_financial_results

# Paths
# Assuming the script is run from project root or as module
# We need to find the data directory relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_FILE = DATA_DIR / "company_descriptions.csv"
OUTPUT_FILE = DATA_DIR / "financial_results_availability.csv"

def load_companies():
    companies = []
    filepath = INPUT_FILE
    if not filepath.exists():
        print(f"Error: Input file not found at {filepath}")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append(row)
    return companies

def load_existing_results():
    existing = set()
    filepath = OUTPUT_FILE
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row['Symbol'])
    return existing

def main():
    parser = argparse.ArgumentParser(description="Check for Financial Results tab on NSE.")
    parser.add_argument("--limit", type=int, help="Limit the number of companies to check (for testing).")
    args = parser.parse_args()

    ensure_header = not os.path.exists(OUTPUT_FILE)
    
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['Symbol', 'Company Name', 'Has Financial Results', 'URL', 'Status Code', 'Error']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if ensure_header:
            writer.writeheader()

        companies = load_companies()
        existing_symbols = load_existing_results()
        
        count = 0
        total = len(companies)
        
        print(f"Found {total} companies. Already checked {len(existing_symbols)}.")

        for company in companies:
            if args.limit and count >= args.limit:
                print(f"Limit of {args.limit} reached.")
                break

            symbol = company.get('Symbol')
            if not symbol or symbol in existing_symbols:
                continue
            
            print(f"[{count+1}/{total}] Checking {symbol}...")
            
            result_row = {
                'Symbol': symbol,
                'Company Name': company.get('Company Name', ''),
                'Has Financial Results': False,
                'URL': '',
                'Status Code': '',
                'Error': ''
            }

            try:
                # Use the scraper function
                response = selenium_fetch_financial_results(symbol)
                
                result_row['Has Financial Results'] = response.get('__available__', False)
                result_row['URL'] = response.get('url', '')
                result_row['Status Code'] = response.get('code', '')
                
                if response.get('__available__'):
                     print(f"  -> FOUND! ({response.get('url')})")
                else:
                     print(f"  -> Not found.")

            except Exception as e:
                print(f"  -> Error: {e}")
                result_row['Error'] = str(e)
            
            # Write immediately to save progress
            writer.writerow(result_row)
            f.flush()
            
            count += 1
            # Respectful delay
            time.sleep(1) 

if __name__ == "__main__":
    main()
