import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nseindia.com/",
}

symbol = "BAJAJHFL"
indexes = ["equities", "sme", "debt"]

s = requests.Session()
# Warmup
s.get("https://www.nseindia.com", headers=headers)

for idx in indexes:
    url = f"https://www.nseindia.com/api/corporates-financial-results?index={idx}&symbol={symbol}"
    print(f"Checking {url}...")
    try:
        res = s.get(url, headers=headers, timeout=10)
        print(f"  Status: {res.status_code}")
        print(f"  Content-Type: {res.headers.get('content-type')}")
        if res.status_code == 200:
            try:
                data = res.json()
                print(f"  Data Type: {type(data)}")
                print(f"  Data Length: {len(data) if isinstance(data, list) else 'N/A'}")
                print(f"  Data Sample: {str(data)[:100]}")
            except:
                print(f"  Not JSON: {res.text[:100]}")
    except Exception as e:
        print(f"  Error: {e}")
