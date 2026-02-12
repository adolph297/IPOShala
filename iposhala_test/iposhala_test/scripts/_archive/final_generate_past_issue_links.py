from datetime import datetime, timezone
from pymongo import UpdateOne
from mongo import ipo_past_master

def build_ipo_link(symbol, security_type):
    if not symbol:
        return None

    if security_type and "SME" in security_type.upper():
        return f"https://www.nseindia.com/market-data/issue-details-sme?symbol={symbol}"

    return f"https://www.nseindia.com/market-data/issue-details?symbol={symbol}"


def generate_links():
    print("🚀 Generating NSE Past Issue links")

    ops = []
    cursor = ipo_past_master.find({})

    count = 0
    for doc in cursor:
        symbol = doc.get("symbol")
        security_type = doc.get("security_type")

        link = build_ipo_link(symbol, security_type)
        if not link:
            continue

        ops.append(
            UpdateOne(
                {"_id": doc["_id"]},
                {
                    "$set": {
                        "nse_detail_url": link,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
        )
        count += 1

    if ops:
        ipo_past_master.bulk_write(ops)
        print(f"✅ Updated {count} IPOs with NSE links")
    else:
        print("⚠️ No IPOs updated")


if __name__ == "__main__":
    generate_links()

