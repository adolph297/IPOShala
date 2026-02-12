
import requests
import pprint

BASE_URL = "http://localhost:8000"
symbol = "GKSL"

print(f">>> Checking Full API data for {symbol} <<<")

try:
    # 1. Check /api/ipos/{symbol}
    print(f"\n--- API /api/ipos/{symbol} ---")
    r1 = requests.get(f"{BASE_URL}/api/ipos/{symbol}", timeout=10)
    if r1.status_code == 200:
        data = r1.json()
        print(f"Keys returned: {list(data.keys())}")
        print(f"Has nse_company? {'nse_company' in data}")
        print(f"Has nse_quote? {'nse_quote' in data}")
    else:
        print(f"Error {r1.status_code}: {r1.text}")

    # 2. Check /api/company/{symbol}/tabs
    print(f"\n--- API /api/company/{symbol}/tabs ---")
    r2 = requests.get(f"{BASE_URL}/api/company/{symbol}/tabs", timeout=10)
    if r2.status_code == 200:
        pprint.pprint(r2.json())
    else:
        print(f"Error {r2.status_code}: {r2.text}")

    # 3. Check /api/company/{symbol}/announcements
    print(f"\n--- API /api/company/{symbol}/announcements ---")
    r3 = requests.get(f"{BASE_URL}/api/company/{symbol}/announcements", timeout=10)
    if r3.status_code == 200:
        ann = r3.json()
        print(f"Announcements count: {len(ann)}")
        if len(ann) > 0:
            pprint.pprint(ann[0])
    else:
        print(f"Error {r3.status_code}: {r3.text}")

except Exception as e:
    print(f"Connection failed: {e}")
