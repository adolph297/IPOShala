import csv
import requests
import time
from urllib.parse import urljoin

INPUT = "data/IPO_transform_.csv"
OUTPUT = "data/IPO_archive_patterns.csv"

BASE = "https://nsearchives.nseindia.com/content/ipo/"

DOC_PATTERNS = {
    "doc_anchor": "ANCHOR_{sym}.zip",
    "doc_rhp": "RHP_{sym}.zip",
    "doc_ratios": "Ratios_Basis_{sym}.zip",
    "doc_bidding": "BIDDING_{sym}.zip",
    "doc_sample": "SAMPLE_{sym}.zip",
    "doc_security_pre": "SECURITY_PRE_{sym}.zip",
    "doc_security_post": "SECURITY_POST_{sym}.zip",
    "doc_anchor_report": "ANCHOR_REPORT_{sym}.zip",
}

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def check_url(url):
    try:
        r = session.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False


with open(INPUT, newline="", encoding="utf-8") as fin:
    reader = csv.DictReader(fin)
    rows = list(reader)
    fields = reader.fieldnames

for i, row in enumerate(rows, start=1):
    symbol = row.get("Symbol")
    if not symbol:
        continue

    symbol = symbol.upper().strip()
    print(f"[{i}/{len(rows)}] Testing {symbol}")

    for col, pattern in DOC_PATTERNS.items():

        if row.get(col):
            continue  # skip if already have link

        candidate = urljoin(BASE, pattern.format(sym=symbol))

        if check_url(candidate):
            row[col] = candidate
            print("   ✔ Found", col)

    time.sleep(0.3)

with open(OUTPUT, "w", newline="", encoding="utf-8") as fout:
    writer = csv.DictWriter(fout, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("✨ Archive pattern extraction complete →", OUTPUT)
