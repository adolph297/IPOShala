from iposhala_test.scrapers.nse_company_dynamic import _safe_get_json, cookie_pool
import json

def debug_alternatives():
    symbol = "RELIANCE"
    s = cookie_pool.get()
    
    endpoints = [
        f"https://www.nseindia.com/api/corporate-share-holdings-master?index=equities&symbol={symbol}",
        f"https://www.nseindia.com/api/share-holding-pattern?index=equities&symbol={symbol}",
        f"https://www.nseindia.com/api/historical/share-holding-pattern?symbol={symbol}"
    ]

    for url in endpoints:
        print(f"Trying URL: {url}")
        try:
            data = _safe_get_json(s, url)
            if data.get("__available__"):
                print("SUCCESS!")
                print("Keys:", data["data"].keys() if data["data"] else "No data key")
                # print(json.dumps(data, indent=2))
                break
            else:
                print(f"Failed (Code: {data.get('code')})")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_alternatives()
