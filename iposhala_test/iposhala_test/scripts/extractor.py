import csv
import requests
import time

INPUT = "data/IPO_Past_Issues_main.m.csv"
OUTPUT = "data/IPO_bidding_centers_updated.csv"

BASE = "https://nsearchives.nseindia.com/content/ipo/"

DOC_PATTERNS = {
    "doc_anchor": "ANCHOR_{}.zip",
    "doc_rhp": "RHP_{}.zip",
    "doc_ratios": "RATIOS_{}.zip",
    "doc_forms": "FORMS_{}.zip",
    "doc_security_pre": "PREANCHOR_PARAMETERS_{}.zip",
    "doc_security_post": "POSTANCHOR_PARAMETERS_{}.zip",
    "doc_bidding": "BIDDING_CENTERS_{}.zip",
}

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Connection": "keep-alive"
})


def url_exists(url):
    try:
        r = session.get(url, stream=True, timeout=6)
        ok = (r.status_code == 200)
        r.close()
        return ok
    except:
        return False


# --- load CSV ---

with open(INPUT, newline="", encoding="utf-8") as fin:

    reader = csv.DictReader(fin)
    rows = list(reader)
    fields = reader.fieldnames

    # ensure all output columns exist
    for col in DOC_PATTERNS.keys():
        if col not in fields:
            fields.append(col)


total = len(rows)

# --- extraction loop ---

for i, row in enumerate(rows, start=1):

    symbol = row.get("Symbol")

    if not symbol:
        continue

    symbol = symbol.upper().strip()

    print(f"\n[{i}/{total}] Processing {symbol}")

    for column, pattern in DOC_PATTERNS.items():

        # skip if already populated
        if row.get(column):
            continue

        url = BASE + pattern.format(symbol)

        if url_exists(url):
            row[column] = url
            print(f"   ✔ {column}")

    # polite delay to avoid NSE throttling
    time.sleep(0.4)


# --- save output ---

with open(OUTPUT, "w", newline="", encoding="utf-8") as fout:

    writer = csv.DictWriter(fout, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("\n✅ Full archive extraction complete →", OUTPUT)
