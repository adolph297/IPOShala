import os
import sys
import csv
import logging
import argparse
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.getcwd())
try:
    from iposhala_test.scripts.mongo import ipo_past_master, ipo_past_issue_info
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
CSV_PATH = os.path.join(os.getcwd(), "iposhala_test", "data", "IPO_bidding_centers_updated.csv")

DOC_MAP = {
    "doc_rhp": "rhp",
    "doc_ratios": "ratios",
    "doc_forms": "forms",
    "doc_security_pre": "pre-anchor",
    "doc_security_post": "post-anchor",
    "doc_bidding": "bidding_centers",
    "Anchor_Allocation_ZIP": "anchor_allocation",
    "ASBA_Circular_PDF": "asba_circular",
    "UPI_ASBA_Video": "upi_asba_video",
    "BHIM_UPI_Registration_Video": "bhim_upi_video"
}

def clean(value):
    if value is None: return None
    v = str(value).strip()
    return v if v else None

def ingest_documents_from_csv():
    """
    Parses the central mapping CSV and hydrates the document objects in MongoDB.
    Acts as the single source of truth for RHP, Draft, and Circular documents.
    """
    if not os.path.exists(CSV_PATH):
        logging.error(f"[DOCUMENTS] Missing critical CSV file at {CSV_PATH}")
        return False
        
    logging.info(f"[DOCUMENTS] Starting ingestion from {CSV_PATH}...")
    
    count, updated = 0, 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            count += 1
            sym = clean(row.get("Symbol"))
            if not sym: continue

            doc_fields = {mongo_key: clean(row.get(csv_col)) for csv_col, mongo_key in DOC_MAP.items()}
            doc_fields = {k: v for k, v in doc_fields.items() if v}
            
            if doc_fields:
                payload = {f"documents.{k}": v for k, v in doc_fields.items()}
                payload["documents_updated_at"] = datetime.now(timezone.utc)
                
                # Execute updates against both collections mirroring legacy logic
                res1 = ipo_past_issue_info.update_one({"symbol": sym}, {"$set": payload}, upsert=True)
                res2 = ipo_past_master.update_one({"symbol": sym}, {"$set": payload}, upsert=True)
                
                if res1.modified_count > 0 or res1.upserted_id or res2.modified_count > 0:
                    updated += 1
                    
    logging.info(f"Processed {count} rows. Updated documents for {updated} IPO records.")
    return True

def restore_database_from_csv():
    """
    Complete MongoDB restoration utility mapping the base IPO entities directly from the validated CSV.
    Drops existing ipo_past_master and recreates.
    """
    if not os.path.exists(CSV_PATH):
        logging.error(f"[RESTORE] Missing document state mapping: {CSV_PATH}")
        return False
        
    logging.info(f"⚠️  Starting FULL state recovery. Dropping ipo_past_master...")
    ipo_past_master.delete_many({})
    
    docs = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sym = clean(row.get("Symbol"))
            if not sym: continue
            
            ipo_docs = {}
            for csv_col, mongo_key in list(DOC_MAP.items())[:6]: # Core Docs
                url = clean(row.get(csv_col))
                ipo_docs[mongo_key] = {"available": bool(url), "source_url": url, "updated_at": datetime.utcnow().isoformat()}
                
            additional_docs = {mongo_key: clean(row.get(csv_col)) for csv_col, mongo_key in list(DOC_MAP.items())[6:] if clean(row.get(csv_col))}
            
            docs.append({
                "symbol": sym.upper(),
                "company_name": clean(row.get("COMPANY NAME")),
                "security_type": clean(row.get("SECURITY TYPE")),
                "issue_price": clean(row.get("ISSUE PRICE")),
                "price_range": clean(row.get("PRICE RANGE")),
                "issue_start_date": clean(row.get("ISSUE START DATE")),
                "issue_end_date": clean(row.get("ISSUE END DATE")),
                "listing_date": clean(row.get("DATE OF LISTING")),
                "ipo_docs": ipo_docs,
                "additional_docs": additional_docs,
                "created_at": datetime.now(timezone.utc),
                "source": "csv_restore"
            })
            
    if docs:
        res = ipo_past_master.insert_many(docs, ordered=False)
        logging.info(f"✅ Successfully completed recovery. Registered {len(res.inserted_ids)} base entity records.")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Unified Documents and Recovery Pipeline")
    parser.add_argument("--ingest", action="store_true", help="Sync Document URLs into active database records.")
    parser.add_argument("--restore", action="store_true", help="WARNING: Drops Master collection and reinflates directly from CSV dataset.")
    args = parser.parse_args()

    if args.ingest:
        ingest_documents_from_csv()
    if args.restore:
        val = input("This will DROP all existing records in ipo_past_master. Are you sure? (y/N): ")
        if val.lower() == 'y': restore_database_from_csv()
        else: logging.info("Restore cancelled.")
        
    if not (args.ingest or args.restore):
        parser.print_help()

if __name__ == "__main__":
    main()
