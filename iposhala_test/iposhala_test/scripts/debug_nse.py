import requests
import time
import json

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/",
}

def create_session():
    s = requests.Session()
    s.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)
    time.sleep(1)
    return s

def test_symbol(symbol):
    s = create_session()
    
    # Try different date ranges
    today = "12-02-2026"
    start_of_year = "01-01-2026"
    
    test_urls = [
        # Standard
        f"https://www.nseindia.com/api/corporate-announcements?symbol={symbol}&index=sme",
        f"https://www.nseindia.com/api/corporate-announcements?symbol={symbol}&index=equities",
        # Date based
        f"https://www.nseindia.com/api/corporate-announcements?symbol={symbol}&index=sme&from_date={start_of_year}&to_date={today}",
        f"https://www.nseindia.com/api/corporate-announcements?symbol={symbol}&index=equities&from_date={start_of_year}&to_date={today}",
        # Without index
        f"https://www.nseindia.com/api/corporate-announcements?symbol={symbol}",
        # Whole SME list
        "https://www.nseindia.com/api/corporate-announcements?index=sme",
    ]
    
    for url in test_urls:
        print(f"\nURL: {url}")
        try:
            # Add Referer for the specific symbol
            headers = NSE_HEADERS.copy()
            headers["Referer"] = f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}"
            
            r = s.get(url, headers=headers, timeout=10)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                try:
                    data = r.json()
                    if isinstance(data, list):
                        print(f"  Count: {len(data)}")
                        if len(data) > 0:
                            # Print first 2 symbols found
                            found_symbols = list(set([item.get('symbol') or item.get('Symbol') for item in data[:20]]))
                            print(f"  Sample symbols in response: {found_symbols[:5]}")
                            # Check if our symbol is in there
                            matches = [item for item in data if (item.get('symbol') or item.get('Symbol') or '').upper() == symbol.upper()]
                            print(f"  Matches for {symbol}: {len(matches)}")
                    else:
                        print(f"  Not a list: {type(data)}")
                except Exception as json_err:
                    print(f"  JSON Error: {json_err}")
                    print(f"  Raw Snippet: {r.text[:100]}")
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    test_symbol("E2ERAIL")
