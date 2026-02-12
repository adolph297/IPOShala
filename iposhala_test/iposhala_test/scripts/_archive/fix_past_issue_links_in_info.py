from datetime import datetime, timezone
from pymongo import UpdateOne
from mongo import ipo_past_issue_info, ipo_past_master

def build_ipo_link(symbol, security_type):
    if not symbol:
        return None

    if security_type and "SME" in security_type.upper():
        return f"https://www.nseindia.com/market-data/issue-details-sme?symbol={symbol}"

    return f"https://www.nseindia.com/market-data/issue-details?symbol={symbol}"


def update_past_issue_links():
    print("🚀 Updating NSE links in ipo_past_issue_info")

    ops = []
    cursor = ipo_past_issue_info.find({})

    count = 0
    for doc in cursor:
        symbol = doc.get("symbol")
        if not symbol:
            continue

        # 🔑 get security_type from master collection
        master = ipo_past_master.find_one({"symbol": symbol})
        security_type = master.get("security_type") if master else None

        link = build_ipo_link(symbol, security_type)
        if not link:
            continue

        ops.append(
            UpdateOne(
                {"_id": doc["_id"]},
                {
                    "$set": {
                        "nse_issue_link": link,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
        )
        count += 1

    if ops:
        ipo_past_issue_info.bulk_write(ops)
        print(f"✅ Updated {count} documents with NSE links")
    else:
        print("⚠️ Nothing updated")


if __name__ == "__main__":
    update_past_issue_links()
