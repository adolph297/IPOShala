import requests
from pymongo import UpdateOne
from mongo import ipo_past_issue_info

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def file_exists(url):
    try:
        r = requests.head(url, headers=HEADERS, timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def discover_archive_links():
    print("🚀 Discovering NSE archive links (safe mode)")

    ops = []

    for doc in ipo_past_issue_info.find({}):
        symbol = doc.get("symbol")
        if not symbol:
            continue

        updates = {}

        # Anchor Allocation ZIP
        anchor_zip = f"https://nsearchives.nseindia.com/content/ipo/ANCHOR_{symbol}.zip"
        if file_exists(anchor_zip):
            updates["documents.anchor_allocation_report_archive"] = anchor_zip

        # Prospectus PDF (optional, rare)
        prospectus_pdf = f"https://nsearchives.nseindia.com/content/ipo/PROSPECTUS_{symbol}.pdf"
        if file_exists(prospectus_pdf):
            updates["documents.prospectus_pdf"] = prospectus_pdf

        if updates:
            ops.append(
                UpdateOne(
                    {"_id": doc["_id"]},
                    {"$set": updates}
                )
            )

    if ops:
        ipo_past_issue_info.bulk_write(ops)
        print(f"✅ Added archive links to {len(ops)} IPOs")
    else:
        print("⚠️ No archive links found")

if __name__ == "__main__":
    discover_archive_links()


