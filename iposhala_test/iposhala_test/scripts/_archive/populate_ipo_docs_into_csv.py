import csv
import time
import requests
import os
from datetime import datetime

# ✅ Mongo (your existing project import)
from iposhala_test.scripts.mongo import ipo_past_master

INPUT_CSV = "iposhala_test/data/IPO_Past_Issues_main.m.csv"
OUTPUT_CSV = "iposhala_test/data/IPO_Past_Issues_main.m.with_docs.csv"

# ✅ checkpoint interval
CHECKPOINT_EVERY = 200

# ✅ refresh NSE session every N symbols (prevents cookie expiry / blocks)
SESSION_REFRESH_EVERY = 100

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nseindia.com/",
}

# ============================================================
# ✅ MODE B (Proxy Streaming) configuration
# ============================================================

DOC_BASE_URL = os.getenv("DOC_BASE_URL", "http://localhost:8000").rstrip("/")

# These are the 7 CSV output columns we must populate
NEW_COLUMNS = [
    "Ratios_Basis_Issue_Price",
    "Red_Herring_Prospectus",
    "Bidding_Centers",
    "Sample_Application_Forms",
    "Security_Parameters_Pre_Anchor",
    "Security_Parameters_Post_Anchor",
    "Anchor_Allocation_Report",
]

# canonical doc_type -> CSV column mapping
DOC_COLUMNS = {
    "ratios": "Ratios_Basis_Issue_Price",
    "rhp": "Red_Herring_Prospectus",
    "bidding-centers": "Bidding_Centers",
    "forms": "Sample_Application_Forms",
    "pre-anchor": "Security_Parameters_Pre_Anchor",
    "post-anchor": "Security_Parameters_Post_Anchor",
    "anchor-allocation": "Anchor_Allocation_Report",
}

# CSV column -> canonical doc_type
COL_TO_DOC_TYPE = {v: k for k, v in DOC_COLUMNS.items()}


def make_backend_doc_url(symbol: str, doc_type: str) -> str:
    symbol = (symbol or "").upper().strip()
    return f"{DOC_BASE_URL}/api/docs/{symbol}/{doc_type}"


def normalize_symbol(symbol: str) -> str:
    return (symbol or "").upper().strip()


def warmup(session: requests.Session):
    session.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)


def safe_get_json(session: requests.Session, url: str, retries: int = 3):
    """
    NSE can return HTML (blocked) even when status=200.
    This function retries and refreshes warmup cookies.
    """
    last_err = None

    for i in range(retries):
        try:
            r = session.get(url, headers=NSE_HEADERS, timeout=20)

            # retry on 401/403
            if r.status_code in (401, 403):
                warmup(session)
                time.sleep(1.5 + i)
                continue

            r.raise_for_status()

            ct = (r.headers.get("content-type") or "").lower()

            # ✅ NSE blocked HTML detection
            if "application/json" not in ct:
                raise Exception(
                    f"Blocked/non-json response ct={ct}, sample={r.text[:200]}"
                )

            return r.json()

        except Exception as e:
            last_err = e
            time.sleep(1.5 + i)  # backoff

            # refresh cookies on retry
            try:
                warmup(session)
            except Exception:
                pass

    raise last_err


def fetch_ipo_docs_from_nse(session: requests.Session, symbol: str) -> dict:
    """
    Extract docs from NSE IPO endpoints.
    Returns dict: { CSV_COLUMN_NAME: NSE_SOURCE_URL }
    """
    sym = normalize_symbol(symbol)

    candidates = [
        "https://www.nseindia.com/api/ipo-past-issue",
        "https://www.nseindia.com/api/ipo-current-issue",
        "https://www.nseindia.com/api/ipo-upcoming-issue",
    ]

    issues = []
    for url in candidates:
        try:
            data = safe_get_json(session, url)
        except Exception:
            continue

        if isinstance(data, list):
            issues.extend([x for x in data if isinstance(x, dict)])
        elif isinstance(data, dict):
            arr = data.get("data") or data.get("result") or []
            if isinstance(arr, list):
                issues.extend([x for x in arr if isinstance(x, dict)])

    issue = next((x for x in issues if normalize_symbol(x.get("symbol")) == sym), None)
    if not issue:
        return {}

    docs = {}

    def put(col, val):
        if val and isinstance(val, str) and val.startswith("http"):
            docs[col] = val

    # ✅ common fields
    put("Red_Herring_Prospectus", issue.get("rhpDocument") or issue.get("rhp") or issue.get("rhpPdf"))
    put("Anchor_Allocation_Report", issue.get("anchorDocument") or issue.get("anchorAllocationReport"))
    put("Ratios_Basis_Issue_Price", issue.get("basisOfIssuePrice") or issue.get("basisOfAllotment"))

    # ✅ documents list fallback
    documents = issue.get("documents") or []
    if isinstance(documents, list):
        for d in documents:
            if not isinstance(d, dict):
                continue

            name = (d.get("name") or d.get("title") or "").lower()
            link = d.get("url") or d.get("link")
            if not link:
                continue

            if "rhp" in name or "red herring" in name:
                put("Red_Herring_Prospectus", link)
            elif "bidding" in name:
                put("Bidding_Centers", link)
            elif "sample application" in name:
                put("Sample_Application_Forms", link)
            elif "security parameters" in name and "pre" in name:
                put("Security_Parameters_Pre_Anchor", link)
            elif "security parameters" in name and "post" in name:
                put("Security_Parameters_Post_Anchor", link)
            elif "anchor allocation" in name:
                put("Anchor_Allocation_Report", link)
            elif "ratios" in name or "basis of issue" in name:
                put("Ratios_Basis_Issue_Price", link)

    return docs


def upsert_ipo_docs_into_mongo(symbol: str, docs_by_column: dict):
    """
    Store NSE source URLs into Mongo for docs backend.
    Even if docs are missing, we store availability=false so backend can respond properly.
    """
    symbol = normalize_symbol(symbol)
    now = datetime.utcnow().isoformat()

    ipo_docs = {}

    # ✅ Always create all 7 keys
    for doc_type in DOC_COLUMNS.keys():
        col = DOC_COLUMNS[doc_type]
        nse_url = (docs_by_column or {}).get(col)

        ipo_docs[doc_type] = {
            "available": bool(nse_url),
            "source_url": nse_url if nse_url else None,
            "updated_at": now,
        }

    ipo_past_master.update_one(
        {"symbol": symbol},
        {
            "$set": {
                "symbol": symbol,
                "ipo_docs": ipo_docs,
                "ipo_docs_last_updated": now,
            }
        },
        upsert=True,
    )


def write_csv(rows, fieldnames):
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    # ✅ add missing columns
    for c in NEW_COLUMNS:
        if c not in fieldnames:
            fieldnames.append(c)

    # ✅ create session once
    session = requests.Session()
    warmup(session)

    total = len(rows)

    for i, row in enumerate(rows, start=1):
        # ✅ refresh session periodically
        if i % SESSION_REFRESH_EVERY == 0:
            session = requests.Session()
            warmup(session)
            print(f"🔄 NSE session refreshed at row {i}")

        symbol = row.get("Symbol") or row.get("SYMBOL") or row.get("symbol")
        sym = normalize_symbol(symbol)
        if not sym:
            continue

        print(f"[{i}/{total}] Fetching docs for {sym}")

        docs = {}
        try:
            docs = fetch_ipo_docs_from_nse(session, sym)
        except Exception as e:
            print("   ❌ NSE fetch failed:", str(e))
            docs = {}

        # ✅ store NSE URLs / availability into Mongo
        try:
            upsert_ipo_docs_into_mongo(sym, docs)
        except Exception as e:
            print("   ⚠️ Mongo update failed:", str(e))

        # ✅ ALWAYS fill backend doc URLs (NO NA EVER)
        for col in NEW_COLUMNS:
            doc_type = COL_TO_DOC_TYPE.get(col)
            if not doc_type:
                continue

            row[col] = make_backend_doc_url(sym, doc_type)

        # ✅ checkpoint save
        if i % CHECKPOINT_EVERY == 0:
            write_csv(rows, fieldnames)
            print(f"✅ checkpoint saved at row {i}")

        time.sleep(0.2)

    # ✅ final save
    write_csv(rows, fieldnames)

    print("\n✅ Done!")
    print("Output written to:", OUTPUT_CSV)


if __name__ == "__main__":
    main()
