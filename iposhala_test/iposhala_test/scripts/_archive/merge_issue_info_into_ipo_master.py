from mongo import ipo_master, ipo_past_issue_info

updated = 0
skipped = 0

cursor = ipo_past_issue_info.find(
    {"normalized_company_name": {"$exists": True}}
)

for doc in cursor:
    norm = doc["normalized_company_name"]

    result = ipo_master.update_one(
        {"normalized_company_name": norm},
        {
            "$set": {
                "issue_information": doc.get("issue_information", {}),
                "documents": doc.get("documents", {}),
                "issue_info_source": doc.get("source"),
            }
        }
    )

    if result.matched_count == 1:
        updated += 1
    else:
        skipped += 1

print(f"[OK] Issue info merge complete | updated={updated} | skipped={skipped}")
