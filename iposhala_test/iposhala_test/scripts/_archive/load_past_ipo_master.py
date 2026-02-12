import pandas as pd
from datetime import datetime, timezone
from mongo import ipo_past_master


def normalize_company_name(name):
    if not name or pd.isna(name):
        return None
    return (
        str(name)
        .lower()
        .strip()
        .replace("&", "and")
        .replace(".", "")
        .replace(",", "")
        .replace("  ", " ")
        .replace(" ", "_")
    )


CSV_PATH = "data/IPO-PastIssue-13-Jan-2026.csv"

df = pd.read_csv(CSV_PATH)

# normalize column names
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]


def col(*names):
    for n in names:
        if n in df.columns:
            return n
    return None


company_col = col("company_name", "company", "issuer_name", "name_of_company")
symbol_col = col("symbol")
sec_col = col("security_type", "segment")
price_col = col("issue_price", "price")
range_col = col("price_range")
start_col = col("issue_start_date", "issue_open_date", "open_date")
end_col = col("issue_end_date", "issue_close_date", "close_date")
list_col = col("date_of_listing", "listing_date")

records = []

for _, row in df.iterrows():
    company_name = row.get(company_col)
    normalized_name = normalize_company_name(company_name)

    records.append({
        "company_name": company_name,
        "normalized_company_name": normalized_name,   # ✅ FIX
        "symbol": row.get(symbol_col),
        "security_type": row.get(sec_col),
        "issue_price": row.get(price_col),
        "price_range": row.get(range_col),
        "issue_start_date": row.get(start_col),
        "issue_end_date": row.get(end_col),
        "listing_date": row.get(list_col),
        "category": "PAST",
        "created_at": datetime.now(timezone.utc),
    })

ipo_past_master.delete_many({})
ipo_past_master.insert_many(records)

print(f"[OK] Inserted {len(records)} past IPO master records")
