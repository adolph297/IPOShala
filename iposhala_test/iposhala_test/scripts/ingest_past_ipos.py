print(">>> RUNNING ingest_past_ipos.py <<<")

import csv
from datetime import datetime
from mongo import ipo_past_master

CSV_PATH = "data/IPO_Past_Issues_main.m.csv"


def clean(value):
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


def normalize_company_name(name):
    if not name:
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


with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        try:
            symbol = clean(row.get("Symbol"))
            company_name = clean(row.get("COMPANY NAME"))

            if not symbol or not company_name:
                continue

            issue_information = {
                "issue_start_date": clean(row.get("ISSUE START DATE")),
                "issue_end_date": clean(row.get("ISSUE END DATE")),
                "listing_date": clean(row.get("DATE OF LISTING")),
                "price_range": clean(row.get("PRICE RANGE")),
                "issue_price": clean(row.get("ISSUE PRICE")),
                "anchor_allocation_zip": clean(row.get("Anchor_Allocation_ZIP")),
                "asba_circular_pdf": clean(row.get("ASBA_Circular_PDF")),
                "upi_asba_video": clean(row.get("UPI_ASBA_Video")),
                "bhim_upi_registration_video": clean(row.get("BHIM_UPI_Registration_Video")),
            }

            issue_information = {k: v for k, v in issue_information.items() if v}

            data = {
                "symbol": symbol,
                "company_name": company_name,
                "normalized_company_name": normalize_company_name(company_name),
                "security_type": clean(row.get("SECURITY TYPE")),
                "exchange": "NSE",
                "issue_information": issue_information,
                "source": "Historical CSV",
                "details_fetched": False,
                "updated_at": datetime.utcnow(),
            }

            ipo_past_master.update_one(
                {"symbol": symbol},
                {"$set": data, "$setOnInsert": {"created_at": datetime.utcnow()}},
                upsert=True
            )

            print(f"[OK] Ingested/Updated -> {symbol}")

        except Exception as e:
            print(f"[ERROR] Failed for symbol {row.get('Symbol')}: {e}")
