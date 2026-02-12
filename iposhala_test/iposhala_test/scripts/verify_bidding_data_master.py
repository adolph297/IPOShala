
from mongo import ipo_past_issue_info, ipo_past_master
import pprint

print(">>> Verifying Bidding Centers Data in BOTH Collections for E2ERAIL <<<")

symbol = "E2ERAIL"

# Check ipo_past_issue_info
print(f"\n--- Checking ipo_past_issue_info for {symbol} ---")
info_doc = ipo_past_issue_info.find_one({"symbol": symbol}, {"_id": 0})
if info_doc and "documents" in info_doc and "rhp" in info_doc["documents"]:
    print("[SUCCESS] Found RHP in ipo_past_issue_info")
else:
    print("[ERROR] RHP missing in ipo_past_issue_info")

# Check ipo_past_master
print(f"\n--- Checking ipo_past_master for {symbol} ---")
master_doc = ipo_past_master.find_one({"symbol": symbol}, {"_id": 0})

if master_doc:
    if "documents" in master_doc and "rhp" in master_doc["documents"]:
        print("[SUCCESS] Found RHP in ipo_past_master")
        print("\nMaster Document Data:")
        pprint.pprint(master_doc)
    else:
        print("[ERROR] RHP missing in ipo_past_master or 'documents' field missing")
        pprint.pprint(master_doc)
else:
    print("[ERROR] No document found in ipo_past_master for E2ERAIL")

# Count total documents in master with bidding info
count = ipo_past_master.count_documents({"bidding_centers_ingested": True})
print(f"\nTotal records in ipo_past_master with bidding centers info: {count}")
