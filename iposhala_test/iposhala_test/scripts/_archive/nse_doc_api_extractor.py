import csv
import time
import requests

INPUT = "data/IPO_transform_.csv"
OUTPUT = "data/IPO_enriched_api.csv"

API_URL = "https://www.nseindia.com/api/ipo-documents?symbol={}"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
}

DOC_MAP = {
    "Anchor Allocation": "doc_anchor",
    "Red Herring Prospectus": "doc_rhp",
    "Bidding Centers": "doc_bidding",
    "Sample Application Forms": "doc_sample",
    "Security Parameters (Pre": "doc_security_pre",
    "Security Parameters (Post": "doc_security_post",
    "Anchor Allocation Report": "doc_anchor_report",
}

session = requests.Session()
session.headers.update(HEADERS)

# warm up NSE session
session.get("https://www.nseindia.com")

def fetch_docs(symbol):

    docs = {}

    try:
        r = session.get(API_URL.format(symbol), timeout=10)

        if r.status_code != 200:
            print("API fail:", symbol)
            return docs

        data = r.json()

        for item in data.get("documents", []):
            label = item.get("label", "")
            url = item.get("url", "")

            for key_text, col in DOC_MAP.items():
                if key_text.lower() in label.lower():
                    docs[col] = url

    except Exception as e:
        print("Error:", symbol, e)

    return docs


with open(INPUT, newline="", encoding="utf-8") as fin:

    reader = csv.DictReader(fin)
    rows = list(reader)
    fields = reader.fieldnames


total = len(rows)

for i, row in enumerate(rows, start=1):

    symbol = row.get("Symbol")

    if not symbol:
        continue

    print(f"[{i}/{total}] Fetching API docs for {symbol}")

    docs = fetch_docs(symbol)

    for col, url in docs.items():
        if not row.get(col):
            row[col] = url

    time.sleep(1.2)


with open(OUTPUT, "w", newline="", encoding="utf-8") as fout:

    writer = csv.DictWriter(fout, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)


print("\n✅ API enrichment complete →", OUTPUT)
