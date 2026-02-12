from datetime import datetime, timezone
from pymongo import UpdateOne
from mongo import ipo_past_issue_info

NSE = "https://www.nseindia.com"

def fix_documents():
    print("🚀 Fixing ipo_past_issue_info (NSE-correct way)")

    ops = []
    for doc in ipo_past_issue_info.find({}):
        symbol = doc.get("symbol")
        if not symbol:
            continue

        update = {
            "nse_issue_page": f"{NSE}/market-data/issue-details?symbol={symbol}",

            "documents_available": {
                "red_herring_prospectus": True,
                "ratios_basis_price": True,
                "bidding_centers": True,
                "sample_application_forms": True,
                "security_parameters_pre_anchor": True,
                "security_parameters_post_anchor": True,
                "anchor_allocation_report": True
            },

            "upi_links": {
                "upi_apps": f"{NSE}/market-data/upi-applications",
                "upi_process_video": f"{NSE}/market-data/upi-process-video",
                "bhim_registration": f"{NSE}/market-data/bhim-registration"
            },

            "static_links": {
                "e_forms": f"{NSE}/invest/e-forms",
                "scsb_list": f"{NSE}/invest/scsb",
                "asba_circular": f"{NSE}/invest/asba-process"
            },

            "updated_at": datetime.now(timezone.utc)
        }

        ops.append(
            UpdateOne(
                {"_id": doc["_id"]},
                {"$set": update}
            )
        )

    ipo_past_issue_info.bulk_write(ops)
    print(f"✅ Fixed {len(ops)} past issue documents")

if __name__ == "__main__":
    fix_documents()
