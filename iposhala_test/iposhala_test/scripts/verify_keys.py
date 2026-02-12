
from mongo import ipo_past_master

symbol = "E2ERAIL"
doc = ipo_past_master.find_one({"symbol": symbol}, {"documents": 1, "_id": 0})
print(f"Keys in 'documents' for {symbol}: {list(doc.get('documents', {}).keys())}")

# Check if 'security_pre' and 'security_post' are there
docs = doc.get("documents", {})
for key in ["security_pre", "security_post", "bidding_centers"]:
    if key in docs:
        print(f"[OK] Key '{key}' exists.")
    else:
        print(f"[INFO] Key '{key}' missing (might be empty in CSV for this symbol).")
