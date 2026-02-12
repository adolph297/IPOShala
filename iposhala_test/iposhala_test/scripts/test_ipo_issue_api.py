import requests
import json
import time

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

def test_ipo_info(symbol, series):
    s = requests.Session()
    # Warmup
    s.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)
    
    url = f"https://www.nseindia.com/api/ipo-issue-information?symbol={symbol}&series={series}"
    print(f"Fetching {url}...")
    
    r = s.get(url, headers=NSE_HEADERS, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2))
        return data
    else:
        print(f"Error: {r.text[:500]}")
    return None

if __name__ == "__main__":
    # Test SME
    test_ipo_info("SAMPOORNA", "SME")
    time.sleep(2)
    test_ipo_info("E2ERAIL", "SME")
    time.sleep(2)
    # Test a recent Mainboard if known
    # test_ipo_info("BAJAJHOUS", "EQ") 
