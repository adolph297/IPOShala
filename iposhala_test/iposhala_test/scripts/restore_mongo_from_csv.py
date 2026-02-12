"""
MongoDB Restoration Script
Clears the ipo_companies collection and reloads all data from IPO_bidding_centers.csv
"""

import csv
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "iposhala")
COLLECTION_NAME = "ipo_past_master"

# CSV file path
CSV_FILE = os.path.join(BASE_DIR, "data", "IPO_bidding_centers_updated.csv")

# Document type mapping from CSV columns to MongoDB structure
DOC_MAP = {
    "doc_rhp": "rhp",
    "doc_ratios": "ratios",
    "doc_forms": "forms",
    "doc_security_pre": "pre-anchor",
    "doc_security_post": "post-anchor",
    "doc_bidding": "bidding-centers",
    "Anchor_Allocation_ZIP": "anchor-allocation",
}


def build_doc_entry(url):
    """Create a document entry with availability status"""
    return {
        "available": bool(url and url.strip()),
        "source_url": url.strip() if url and url.strip() else None,
        "updated_at": datetime.utcnow().isoformat(),
    }


def parse_csv_row(row):
    """Transform CSV row into MongoDB document"""
    now = datetime.utcnow().isoformat()
    
    # Build ipo_docs structure
    ipo_docs = {}
    for csv_col, mongo_key in DOC_MAP.items():
        url = row.get(csv_col, "").strip()
        ipo_docs[mongo_key] = build_doc_entry(url)
    
    # Build additional docs
    additional_docs = {}
    if row.get("ASBA_Circular_PDF"):
        additional_docs["asba_circular"] = row["ASBA_Circular_PDF"].strip()
    if row.get("UPI_ASBA_Video"):
        additional_docs["upi_asba_video"] = row["UPI_ASBA_Video"].strip()
    if row.get("BHIM_UPI_Registration_Video"):
        additional_docs["bhim_upi_video"] = row["BHIM_UPI_Registration_Video"].strip()
    
    # Create MongoDB document
    document = {
        "symbol": row.get("Symbol", "").strip().upper(),
        "company_name": row.get("COMPANY NAME", "").strip(),
        "security_type": row.get("SECURITY TYPE", "").strip(),
        "issue_price": row.get("ISSUE PRICE", "").strip(),
        "price_range": row.get("PRICE RANGE", "").strip(),
        "issue_start_date": row.get("ISSUE START DATE", "").strip(),
        "issue_end_date": row.get("ISSUE END DATE", "").strip(),
        "listing_date": row.get("DATE OF LISTING", "").strip(),
        "ipo_docs": ipo_docs,
        "additional_docs": additional_docs,
        "created_at": now,
        "updated_at": now,
    }
    
    return document


def main():
    print("=" * 60)
    print("MongoDB Restoration from CSV")
    print("=" * 60)
    print(f"MongoDB URI: {MONGO_URI}")
    print(f"Database: {DB_NAME}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"CSV File: {CSV_FILE}")
    print()
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE):
        print(f"❌ ERROR: CSV file not found at {CSV_FILE}")
        return
    
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Test connection
        client.server_info()
        print("✅ Connected to MongoDB successfully")
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to MongoDB: {e}")
        return
    
    # Count existing documents
    existing_count = collection.count_documents({})
    print(f"📊 Existing documents in collection: {existing_count}")
    
    # Clear existing collection
    if existing_count > 0:
        print(f"⚠️  Dropping existing collection '{COLLECTION_NAME}'...")
        collection.drop()
        print("✅ Collection dropped")
    
    # Read and parse CSV
    print(f"\n📖 Reading CSV file...")
    documents = []
    skipped = 0
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader, 1):
                symbol = row.get("Symbol", "").strip()
                
                if not symbol:
                    skipped += 1
                    continue
                
                doc = parse_csv_row(row)
                documents.append(doc)
                
                if i % 100 == 0:
                    print(f"  Processed {i} rows...")
        
        print(f"✅ Parsed {len(documents)} valid records from CSV")
        if skipped > 0:
            print(f"⚠️  Skipped {skipped} rows (missing symbol)")
    
    except Exception as e:
        print(f"❌ ERROR: Failed to read CSV: {e}")
        return
    
    # Insert documents into MongoDB
    if documents:
        print(f"\n💾 Inserting {len(documents)} documents into MongoDB...")
        try:
            result = collection.insert_many(documents, ordered=False)
            print(f"✅ Successfully inserted {len(result.inserted_ids)} documents")
        except Exception as e:
            print(f"❌ ERROR: Failed to insert documents: {e}")
            return
    else:
        print("⚠️  No documents to insert")
        return
    
    # Verify insertion
    final_count = collection.count_documents({})
    print(f"\n📊 Final document count: {final_count}")
    
    # Show sample document
    print("\n📄 Sample document:")
    sample = collection.find_one()
    if sample:
        print(f"  Symbol: {sample.get('symbol')}")
        print(f"  Company: {sample.get('company_name')}")
        print(f"  Security Type: {sample.get('security_type')}")
        print(f"  Issue Price: {sample.get('issue_price')}")
        print(f"  Documents available:")
        for doc_type, doc_info in sample.get('ipo_docs', {}).items():
            status = "✓" if doc_info.get('available') else "✗"
            print(f"    {status} {doc_type}")
    
    print("\n" + "=" * 60)
    print("✅ MongoDB restoration completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
