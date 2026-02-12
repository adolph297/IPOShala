import requests
import json
import time
from iposhala_test.scrapers.nse_company_dynamic import cookie_pool

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.nseindia.com/",
}

def test_url(url):
    print(f"\n--- Testing: {url} ---")
    s = cookie_pool.get()
    try:
        r = s.get(url, headers=NSE_HEADERS, timeout=20)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print(f"Received list with {len(data)} items.")
                if len(data) > 0:
                    print("Sample:", json.dumps(data[0], indent=2))
            else:
                keys = list(data.keys())
                print(f"Received dict with keys: {keys}")
                # Print sample of a key that looks like a list
                for k in keys:
                    if isinstance(data[k], list) and len(data[k]) > 0:
                        print(f"Sample from '{k}':", json.dumps(data[k][0], indent=2))
                        break
        else:
            print(f"Body: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 1. Past Issues (Mainboard)
    test_url("https://www.nseindia.com/api/ipo-past-issues?index=equities")
    # 2. Past Issues (SME)
    test_url("https://www.nseindia.com/api/ipo-past-issues?index=sme")
    # 3. Current Issues (to see schema)
    test_url("https://www.nseindia.com/api/ipo-current-issue")
