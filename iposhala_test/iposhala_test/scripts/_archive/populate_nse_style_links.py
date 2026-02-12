from datetime import datetime, timezone
from pymongo import UpdateOne
from mongo import ipo_past_issue_info

NSE = "https://www.nseindia.com"

def build_links(symbol):
    return {
        "documents": {
            "ratios": f"{NSE}/companies-listing/public-issues/issue-ratios?symbol={symbol}",
            "red_herring_prospectus": f"{NSE}/companies-listing/public-issues/issue-documents?symbol={symbol}",
            "bidding_centers": f"{NSE}/companies-listing/public-issues/bidding-centres?symbol={symbol}",
            "sample_application_forms": f"{NSE}/companies-listing/public-issues/sample-forms?symbol={symbol}",
            "security_parameters_pre_anchor": f"{NSE}/companies-listing/public-issues/security-parameters?symbol={symbol}&type=PRE",
            "security_parameters_post_anchor": f"{NSE}/companies-listing/public-issues/security-parameters?symbol={symbol}&type=POST",
            "anchor_allocation_report": f"{NSE}/companies-listing/public-issues/anchor-allocation?symbol={symbol}"
        },
        "upi_links": {
            "upi_apps": f"{NSE}/market-data/upi-applications",
            "upi_process_video": f"{NSE}/market-data/upi-process-video",
            "bhim_registration": f"{NSE}/market-data/bhim-registration"
        },
        "other_links": {
            "e_forms": f"{NSE}/invest/e-forms",
            "scsb_list": f"{NSE}/invest/scsb",
            "asba_circular": f"{NSE}/invest/asba-process"
        },
        "nse_issue_page": f"{NSE}/market-data/issue-details?symbol={symbol}"
    }

def populate_links():
    print("🚀 Populating NSE-style links")

    ops = []
    for doc in ipo_past_issue_info.find({}):
        symbol = doc.get("symbol")
        if not symbol:
            continue

        ops.append(
            UpdateOne(
                {"_id": doc["_id"]},
                {
                    "$set": {
                        **build_links(symbol),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
        )

    ipo_past_issue_info.bulk_write(ops)
    print(f"✅ Updated {len(ops)} IPO documents")

if __name__ == "__main__":
    populate_links()
