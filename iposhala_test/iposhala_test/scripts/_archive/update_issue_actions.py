from datetime import datetime, timezone
from pymongo import UpdateOne
from mongo import ipo_past_issue_info

# 🔹 PUT YOUR OWN VIDEO LINKS HERE
YOUR_UPI_ASBA_VIDEO = "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
YOUR_BHIM_VIDEO = "https://www.youtube.com/watch?v=YOUR_VIDEO_ID_2"

def update_issue_actions():
    print("🚀 Updating issue actions (safe update, no deletions)")

    ops = []

    for doc in ipo_past_issue_info.find({}):
        symbol = doc.get("symbol")
        if not symbol:
            continue

        update_fields = {
            # 🔹 Actions for documents (instead of broken NSE links)
            "document_actions": {
                "ratios_basis_price": "OPEN_NSE_ISSUE_PAGE",
                "red_herring_prospectus": "OPEN_NSE_ISSUE_PAGE",
                "bidding_centers": "OPEN_NSE_ISSUE_PAGE",
                "sample_application_forms": "OPEN_NSE_ISSUE_PAGE",
                "security_parameters_pre_anchor": "OPEN_NSE_ISSUE_PAGE",
                "security_parameters_post_anchor": "OPEN_NSE_ISSUE_PAGE",
                "anchor_allocation_report": "OPEN_NSE_ISSUE_PAGE"
            },

            # 🔹 Replace ONLY video links with your own working videos
            "upi_links.upi_process_video": YOUR_UPI_ASBA_VIDEO,
            "upi_links.bhim_registration": YOUR_BHIM_VIDEO,

            # 🔹 Meta
            "updated_at": datetime.now(timezone.utc)
        }

        ops.append(
            UpdateOne(
                {"_id": doc["_id"]},
                {"$set": update_fields}
            )
        )

    if ops:
        ipo_past_issue_info.bulk_write(ops)
        print(f"✅ Updated {len(ops)} documents")
    else:
        print("⚠️ No documents updated")

if __name__ == "__main__":
    update_issue_actions()
