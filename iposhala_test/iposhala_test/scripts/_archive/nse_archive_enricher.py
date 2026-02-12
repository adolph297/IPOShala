import csv
import requests
import time

INPUT = "data/IPO_transform_.csv"
OUTPUT = "data/IPO_archive_enriched.csv"

BASE = "https://nsearchives.nseindia.com/content/ipo/"

DOC_PATTERNS = {
    "doc_anchor": "ANCHOR_{sym}.zip",
    "doc_rhp": "RHP_{sym}.pdf",
    "doc_bidding": "BIDDING_{sym}.pdf",
    "doc_sample": "SAMPLE_{sym}.pdf",
    "doc_security_pre": "SECURITY_PRE_{sym}.pdf",
    "doc_security_post": "SECURITY_POST_{sym}.pdf",
    "doc_anchor_report": "ANCHOR_REPORT_{sym}.pdf",
}

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def exists(url):
    try:
        r = session.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False


with open(INPUT, newline="", encoding="utf-8") as fin:
    reader = csv.DictReader(fin)
    rows = list(reader)
    fields = reader.fieldnames


total = len(rows)

for i, row in enumerate(rows, start=1):

    symbol = row.get("Symbol")

    if not symbol:
        continue

    symbol = symbol.strip().upper()

    print(f"[{i}/{total}] Checking archive for {symbol}")

    for col, pattern in DOC_PATTERNS.items():

        if row.get(col):
            continue

        url = BASE + pattern.format(sym=symbol)

        if exists(url):
            row[col] = url
            print("   ✔", col)

    time.sleep(0.5)


with open(OUTPUT, "w", newline="", encoding="utf-8") as fout:
    writer = csv.DictWriter(fout, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("\n✅ Archive enrichment complete →", OUTPUT)
