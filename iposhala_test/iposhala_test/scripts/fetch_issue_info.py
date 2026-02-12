import requests
from datetime import datetime, timezone
from mongo import ipo_past_master, ipo_past_issue_info

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

session = requests.Session()
session.headers.update(HEADERS)

# -------------------------------
# Helpers
# -------------------------------

def url_exists(url):
    try:
        r = session.head(url, timeout=10)
        return r.status_code == 200
    except:
        return False


def build_documents(symbol):
    candidates = {
        "rhp": f"https://nsearchives.nseindia.com/content/ipo/{symbol}_RHP.pdf",
        "prospectus": f"https://nsearchives.nseindia.com/content/ipo/{symbol}_Prospectus.pdf",
        "drhp": f"https://nsearchives.nseindia.com/content/ipo/{symbol}_DRHP.pdf",
    }

    documents = {}
    for key, url in candidates.items():
        if url_exists(url):
            documents[key] = url

    return documents


# -------------------------------
# Main logic (MongoDB only)
# -------------------------------

symbols = ipo_past_master.distinct(
    "symbol",
    {"details_fetched": {"$ne": True}}
)

for symbol in symbols:
    try:
        if not symbol:
            continue

        master = ipo_past_master.find_one({"symbol": symbol})
        if not master:
            continue

        issue_information = {
            "issue_start_date": master.get("issue_start_date"),
            "issue_end_date": master.get("issue_end_date"),
            "price_range": master.get("price_range"),
            "issue_price": master.get("issue_price"),
            "security_type": master.get("security_type"),
            "listing_date": master.get("listing_date"),
        }

        issue_information = {k: v for k, v in issue_information.items() if v}

        documents = build_documents(symbol)

        data = {
            "symbol": symbol,
            "company_name": master.get("company_name"),
            "normalized_company_name": master.get("normalized_company_name"),
            "issue_information": issue_information,
            "documents": documents,
            "source": "NSE + Historical CSV",
            "fetched_at": datetime.now(timezone.utc),
        }

        ipo_past_issue_info.update_one(
            {"symbol": symbol},
            {"$set": data},
            upsert=True
        )

        # ✅ Mark as fetched
        ipo_past_master.update_one(
            {"symbol": symbol},
            {"$set": {"details_fetched": True}}
        )

        print(f"[OK] Clean data stored -> {symbol}")

    except Exception as e:
        print(f"[ERROR] Failed for {symbol}: {e}")
