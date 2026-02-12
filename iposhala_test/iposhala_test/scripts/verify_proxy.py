
import requests
from mongo import ipo_past_master

print(">>> Verifying Backend Document Proxy (GET) <<<")

BASE_URL = "http://localhost:8000"
symbol = "E2ERAIL"
doc_type = "rhp"

# First, check MongoDB directly to see what we expect
doc = ipo_past_master.find_one({"symbol": symbol}, {"documents": 1, "_id": 0})
print(f"MongoDB documents for {symbol}: {doc}")

url = f"{BASE_URL}/api/docs/{symbol}/{doc_type}"
print(f"Testing URL: {url}")

try:
    response = requests.get(url, timeout=15)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        ct = response.headers.get('Content-Type', '').lower()
        if "pdf" in ct or "octet-stream" in ct:
            print(f"[SUCCESS] Proxy successfully reached the document.")
        else:
            print(f"[INFO] Response Body (likely JSON): {response.text[:200]}")
    else:
        print(f"[ERROR] Proxy returned status {response.status_code}")
        print(f"Response Body: {response.text}")

except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
