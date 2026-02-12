import csv
from mongo import ipo_past_master

OUTPUT_FILE = "past_issues_with_links.csv"


def build_ipo_link(symbol, security_type):
    if not symbol:
        return ""

    if security_type and "SME" in security_type.upper():
        return f"https://www.nseindia.com/market-data/issue-details-sme?symbol={symbol}"

    return f"https://www.nseindia.com/market-data/issue-details?symbol={symbol}"


def fetch_past_issues_and_write_file():
    print("🚀 Generating Past Issues file WITH NSE links")

    cursor = ipo_past_master.find({"category": "PAST"})

    rows = []
    for doc in cursor:
        link = build_ipo_link(
            doc.get("symbol"),
            doc.get("security_type")
        )

        rows.append({
            "company_name": doc.get("company_name"),
            "symbol": doc.get("symbol"),
            "security_type": doc.get("security_type"),
            "issue_start_date": doc.get("issue_start_date"),
            "issue_end_date": doc.get("issue_end_date"),
            "listing_date": doc.get("listing_date"),
            "nse_detail_url": link
        })

    if not rows:
        print("❌ No past issues found")
        return

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Past Issues file created: {OUTPUT_FILE}")
    print(f"✅ Total records: {len(rows)}")


if __name__ == "__main__":
    fetch_past_issues_and_write_file()

