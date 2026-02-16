from iposhala_test.scrapers.nse_company_dynamic import _safe_get_json, cookie_pool
import json

def debug_quote():
    symbol = "RELIANCE"
    print(f"Fetching QUOTE for {symbol} to verify cookies...")
    try:
        s = cookie_pool.get()
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        data = _safe_get_json(s, url)
        print("Fetch result:")
        # Print only keys to avoid massive output
        if data.get("data"):
            print("Keys:", data["data"].keys())
            print("Successfully fetched quote data!")
        else:
            print("Failed to fetch data:", data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_quote()
