import requests
import json

def verify_apis():
    symbols = ['ADVANCE', 'JKIPL', 'BMWVENTLTD', 'HDFC BANK', 'E2ERAIL']
    base_url = "http://127.0.0.1:8000/api/company"
    
    endpoints = [
        "shareholding-pattern",
        "annual-reports",
        "event-calendar"
    ]
    
    for symbol in symbols:
        print(f"\n=== Verification for {symbol} ===")
        for ep in endpoints:
            url = f"{base_url}/{symbol}/{ep}"
            try:
                res = requests.get(url)
                if res.status_code == 200:
                    data = res.json()
                    count = len(data) if isinstance(data, list) else (1 if data else 0)
                    print(f"[{ep}]: OK. Count/Exists: {count}")
                else:
                    print(f"[{ep}]: FAILED (Status: {res.status_code})")
            except Exception as e:
                print(f"[{ep}]: ERROR: {e}")

if __name__ == "__main__":
    verify_apis()
