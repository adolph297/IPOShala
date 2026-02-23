from extract_financials_offline import extract_financials, WEBSITES
import json

targets = ["EXCELSOFT", "CAPILLARY", "FUJIYAMA"]

print(f"Testing {len(targets)} websites...")

for symbol in targets:
    website = WEBSITES.get(symbol)
    if not website: continue
    
    print(f"\nProcessing {symbol} ({website})...")
    try:
        results = extract_financials(symbol, website)
        if results:
            print(f"SUCCESS! Found {len(results)} results for {symbol}")
            print(json.dumps(results[:2], indent=2))
        else:
            print(f"No results for {symbol}")
    except Exception as e:
        print(f"Error for {symbol}: {e}")
