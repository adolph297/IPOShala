import requests
from datetime import datetime, date, timezone
from mongo import ipo_live_upcoming

# 1️⃣ NSE API URL (example – keep your real one if different)
url = "https://www.nseindia.com/api/ipo-current-issue"

# 2️⃣ Headers (MANDATORY for NSE)
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/"
}

# 3️⃣ Session (important for NSE cookies)
session = requests.Session()
session.get("https://www.nseindia.com", headers=headers)

# 4️⃣ API call
response = session.get(url, headers=headers)
response.raise_for_status()

# 5️⃣ JSON parsing ✅ THIS WAS MISSING
data = response.json()

# 6️⃣ Extract items safely
items = data
print(f"Total IPO records received from NSE: {len(items)}")

if not items:
    print("No IPO data received from NSE API")

count = 0
today = date.today()

for item in items:
    try:
        start_dt = datetime.strptime(item["issueStartDate"], "%d-%b-%Y")
        end_dt = datetime.strptime(item["issueEndDate"], "%d-%b-%Y")
    except Exception:
        continue

    if today < start_dt.date():
        status = "UPCOMING"
    elif start_dt.date() <= today <= end_dt.date():
        status = "LIVE"
    else:
        continue

    ipo_live_upcoming.insert_one({
        "company_name": item.get("companyName"),
        "symbol": item.get("symbol"),
        "security_type": item.get("marketType"),
        "issue_start_date": start_dt,
        "issue_end_date": end_dt,
        "price_range": item.get("priceBand"),
        "status": status,
        "issue_size": item.get("issueSize"),
        "source": "nse_api",
        "last_updated": datetime.now(timezone.utc)
    })
    count += 1

print(f"Inserted {count} LIVE / UPCOMING IPOs into MongoDB")
