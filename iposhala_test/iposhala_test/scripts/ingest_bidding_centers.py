
import csv
from datetime import datetime
from mongo import ipo_past_issue_info, ipo_past_master

import os

# Adjust path if needed, assuming running from backend root
CSV_PATH = "data/IPO_bidding_centers_updated.csv"

def clean(value):
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None

def ingest_bidding_centers():
    print(">>> RUNNING ingest_bidding_centers.py <<<")
    
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] CSV file not found at: {CSV_PATH}")
        return

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        count = 0
        updated_count = 0

        for row in reader:
            count += 1
            symbol = clean(row.get("Symbol"))
            company_name = clean(row.get("COMPANY NAME"))

            if not symbol:
                continue

            # Fields to extract
            doc_fields = {
                "rhp": clean(row.get("doc_rhp")),
                "ratios": clean(row.get("doc_ratios")),
                "forms": clean(row.get("doc_forms")),
                "security_pre": clean(row.get("doc_security_pre")),
                "security_post": clean(row.get("doc_security_post")),
                "bidding_centers": clean(row.get("doc_bidding")),
                # Also include other useful links if they aren't already captured properly
                "anchor_allocation": clean(row.get("Anchor_Allocation_ZIP")),
                "asba_circular": clean(row.get("ASBA_Circular_PDF")),
                "upi_asba_video": clean(row.get("UPI_ASBA_Video")),
                "bhim_upi_video": clean(row.get("BHIM_UPI_Registration_Video"))
            }

            # Remove empty fields
            doc_fields = {k: v for k, v in doc_fields.items() if v}

            if not doc_fields:
                continue

            # crypto/stock/etc symbols might differ, but we rely on 'Symbol' column
            
            # Prepare update operation
            # We want to merge these into the 'documents' field.
            # MongoDB $set with dot notation allows updating/adding specific fields within a document
            
            update_fields = {}
            for key, value in doc_fields.items():
                update_fields[f"documents.{key}"] = value
                
            # Also update last_updated or source if needed
            update_fields["bidding_centers_ingested"] = True
            update_fields["updated_at"] = datetime.utcnow()

            # We assume the basic record might exist in ipo_past_issue_info or master.
            # If fetch_issue_info.py hasn't run yet, ipo_past_issue_info might be empty for this symbol.
            # We should try to ensure the record exists.
            
            # First, check if valid symbol in master (optional but good practice)
            # master_record = ipo_past_master.find_one({"symbol": symbol})
            # if not master_record:
            #    print(f"[WARN] Symbol {symbol} not found in master. Skipping.")
            #    continue

            # Update ipo_past_issue_info
            result = ipo_past_issue_info.update_one(
                {"symbol": symbol},
                {"$set": update_fields},
                upsert=True 
            )

            # Update ipo_past_master (User Request)
            result_master = ipo_past_master.update_one(
                {"symbol": symbol},
                {"$set": update_fields},
                upsert=True
            )
            
            if result.modified_count > 0 or result.upserted_id or result_master.modified_count > 0:
                updated_count += 1
                # print(f"[OK] Updated docs for {symbol}")

    print(f"Processed {count} rows.")
    print(f"Updated {updated_count} IPO records with bidding/document links.")

if __name__ == "__main__":
    ingest_bidding_centers()
