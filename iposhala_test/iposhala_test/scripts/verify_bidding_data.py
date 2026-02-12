
from mongo import ipo_past_issue_info
import pprint

print(">>> Verifying Bidding Centers Data for E2ERAIL <<<")

# Find specific document
sample = ipo_past_issue_info.find_one({"symbol": "E2ERAIL"}, {"_id": 0})

if sample:
    print(f"\n[SUCCESS] Found ingested record for symbol: {sample.get('symbol')}")
    print("\nDocument Data:")
    pprint.pprint(sample)
    
    # Check if specific fields exist
    docs = sample.get("documents", {})
    if "rhp" in docs and "ratios" in docs and "forms" in docs:
        print("\n[VERIFIED] Critical document links (RHP, Ratios, Forms) are present.")
    else:
        print("\n[WARNING] Some document links might be missing.")
else:
    print("\n[ERROR] No document found for E2ERAIL")
