from iposhala_test.scripts.mongo import ipo_past_master

result = ipo_past_master.update_many(
    {},
    {"$unset": {
        "nse_company_dynamic_error": "",
        "nse_company_dynamic_fetched": "",
        "nse_company_dynamic_updated_at": ""
    }}
)

print("✅ Removed old step4 fields from", result.modified_count, "documents")
