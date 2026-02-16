from iposhala_test.scrapers.nse_company_dynamic import selenium_fetch_shareholding_pattern
import json

def debug_fetch():
    symbol = "RELIANCE"
    print(f"Fetching shareholding pattern for {symbol}...")
    try:
        data = selenium_fetch_shareholding_pattern(symbol)
        print("Fetch result:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_fetch()
