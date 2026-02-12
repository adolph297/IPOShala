from datetime import datetime, timezone
from mongo import ipo_past_master, ipo_master

inserted = 0
skipped = 0

cursor = ipo_past_master.find({})

print("DEBUG sample doc from ipo_past_master:", ipo_past_master.find_one())


for doc in cursor:
    key = doc.get("normalized_company_name")

    key = str(key).strip() if key else None
    if not key:
        skipped += 1
        continue
    
    ipo_doc = {
        "company_name": doc.get("company_name"),
        "normalized_company_name": key,
        "symbol": doc.get("symbol"),
        "security_type": doc.get("security_type"),

        "category": "PAST",

        "issue_price": doc.get("issue_price"),
        "price_range": doc.get("price_range"),
        "issue_size": doc.get("issue_size"),

        "issue_start_date": doc.get("issue_start_date"),
        "issue_end_date": doc.get("issue_end_date"),
        "listing_date": doc.get("listing_date"),

        "documents": {},
        "issue_information": {},

        "source_flags": {
            "has_historical": True,
            "has_live": False,
            "has_documents": False
        },

        "created_at": doc.get("created_at"),
        "last_updated": datetime.now(timezone.utc)
    }

    try:
        ipo_master.insert_one(ipo_doc)
        inserted += 1
    except Exception:
        # duplicate due to unique index → safe skip
        skipped += 1

print(f"[OK] Historical merge complete | inserted={inserted} | skipped={skipped}")
