import csv
import os
import requests
import time
from datetime import datetime

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "IPO_bidding_centers_updated.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "IPO_bidding_centers_updated.csv")

# NSE Base URL
NSE_ARCHIVE_BASE = "https://nsearchives.nseindia.com/content/ipo/"

# Constants identified from existing data
CONSTANTS = {
    "ASBA_Circular_PDF": "https://archives.nseindia.com/content/circulars/IPO53197.pdf",
    "UPI_ASBA_Video": "https://www.youtube.com/watch?v=UJ394m2Q3rg",
    "BHIM_UPI_Registration_Video": "https://www.youtube.com/watch?v=cIUJOIH0x4c&feature=youtu.be"
}

# Documentation patterns to check
# Format: column_name: (pattern, [extensions])
DOC_PATTERNS = {
    "Anchor_Allocation_ZIP": "ANCHOR_{sym}.zip",
    "doc_rhp": "RHP_{sym}.zip",
    "doc_ratios": "RATIOS_{sym}.zip",
    "doc_forms": "FORMS_{sym}.zip",
    "doc_security_pre": "SECURITY_PRE_{sym}.pdf",
    "doc_security_post": "SECURITY_POST_{sym}.pdf",
    "doc_bidding": "BIDDING_{sym}.pdf"
}

# Reuse headers from other scripts
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

session = requests.Session()

def exists(url):
    """Check if a URL exists using a HEAD request"""
    try:
        r = session.head(url, headers=HEADERS, timeout=10)
        return r.status_code == 200
    except Exception:
        return False

def check_alternative_extensions(sym, pattern):
    """If original extension fails, try common alternatives (zip/pdf)"""
    # Simply swap .zip and .pdf in the pattern
    if ".zip" in pattern:
        alt = pattern.replace(".zip", ".pdf")
    else:
        alt = pattern.replace(".pdf", ".zip")
    
    url = NSE_ARCHIVE_BASE + alt.format(sym=sym)
    if exists(url):
        return url
    return None

def main():
    print(f"🚀 Starting Link Discovery for {CSV_PATH}")
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: CSV not found at {CSV_PATH}")
        return

    rows = []
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"📊 Loaded {len(rows)} IPO entries.")
    
    updated_count = 0
    total_found = 0

    # Use session with warmup
    print("🍪 Warming up NSE session...")
    session = requests.Session()
    session.headers.update(HEADERS) # Use existing HEADERS constant
    try:
        session.get("https://www.nseindia.com", timeout=15)
        # Optional: second hit to nsearchives to prime it
        session.get("https://nsearchives.nseindia.com", timeout=15)
    except Exception: # Catch any exception during warmup
        pass

    # Limit to first 50 IPOs (to cover E2ERAIL at index 30)
    new_ipos_to_process = rows[:50]
    print(f"🎯 Targeted processing: First 50 IPOs.")

    for i, row in enumerate(new_ipos_to_process, start=1):
        symbol = row.get("Symbol", "").strip().upper()
        if not symbol:
            continue

        print(f"[{i}/{len(new_ipos_to_process)}] Processing NEW IPO: {symbol}...", end="\r")
        row_updated = False

        # 1. Apply Constants if missing
        for col, val in CONSTANTS.items():
            if not row.get(col):
                row[col] = val
                row_updated = True

        # 2. Discover Documents (RHP, Anchor, etc.)
        for col, pattern in DOC_PATTERNS.items():
            if row.get(col):
                continue
            
            # Construct URL
            url = f"{NSE_ARCHIVE_BASE}{pattern.format(sym=symbol)}"
            
            try:
                # Try with timeout and follow redirects
                res = session.head(url, timeout=12, allow_redirects=True)
                
                if res.status_code == 200:
                    row[col] = url
                    row_updated = True
                    total_found += 1
                    print(f"\n  ✅ Found {col}: {url}")
                elif res.status_code == 404:
                    # Try alternative extension if zip failed
                    ext_to_check = ".pdf" if ".zip" in url else ".zip"
                    alt_url = url.replace(".zip", ".pdf") if ".zip" in url else url.replace(".pdf", ".zip")
                    
                    res_alt = session.head(alt_url, timeout=12, allow_redirects=True)
                    if res_alt.status_code == 200:
                        row[col] = alt_url
                        row_updated = True
                        total_found += 1
                        print(f"\n  ✅ Found {col}: {alt_url}")
            except Exception:
                pass

        if row_updated:
            updated_count += 1
        
        # Throttling to be nice to NSE
        if row_updated:
            time.sleep(0.1)

    print(f"\n✅ Discovery complete!")
    print(f"📈 Updated {updated_count} IPO rows.")
    print(f"🔗 Found {total_found} new document links.")

    # Save results
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"💾 Results saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
