import requests
import json
import time
from iposhala_test.scrapers.nse_company_dynamic import cookie_pool

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.nseindia.com/",
}

def test_symbol(symbol):
    s = cookie_pool.get()
    urls = [
        f"https://www.nseindia.com/api/ipo-master?symbol={symbol}",
        f"https://www.nseindia.com/api/ipo-detail?symbol={symbol}&series=SME",
        f"https://www.nseindia.com/api/ipo-detail?symbol={symbol}&series=EQ",
    ]
    
    print(f"\n>>> TESTING {symbol} <<<")
    for url in urls:
        try:
            r = s.get(url, headers=NSE_HEADERS, timeout=10)
            print(f"{url} -> {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error {url}: {e}")

if __name__ == "__main__":
    test_symbol("E2ERAIL")
    test_symbol("MARUSHIKA")
    test_symbol("SAMPOORNA")
