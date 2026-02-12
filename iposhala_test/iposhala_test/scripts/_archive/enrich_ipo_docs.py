import csv
import time
import requests
from bs4 import BeautifulSoup

INPUT = "data/IPO_transform_.csv"
OUTPUT = "data/IPO_enriched.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
}

DOC_LABELS = {
    "Anchor Allocation": "doc_anchor",
    "Red Herring Prospectus": "doc_rhp",
    "Bidding Centers": "doc_bidding",
    "Sample Application Forms": "doc_sample",
    "Security Parameters (Pre": "doc_security_pre",
    "Security Parameters (Post": "doc_security_post",
    "Anchor Allocation Report": "doc_anchor_report",
}

BASE_URL = "https://www.nseindia.com/market-data/ipos"

session = requests.Session()
session.headers.update(HEADERS)

def fetch_doc_links(symbol):

    url = f"{BASE_URL}/{symbol}"

    try:
        r = session.get(url, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        docs = {}

        for a in soup.find_all("a", href=True):

            text = a.text.strip()

            for label, key in DOC_LABELS.items():
                if label.lower() in text.lower():
                    docs[key] = a["href"]

        return docs

    except Exception as e:
        print("Error fetching:", symbol, e)
        return {}


with open(INPUT, newline="", encoding="utf-8") as fin:

    reader = csv.DictReader(fin)
    rows = list(reader)
    fields = reader.fieldnames


for row in rows:

    symbol = row.get("Symbol")

    if not symbol:
        continue

    print(f"\nFetching docs for {symbol}")

    docs = fetch_doc_links(symbol)

    for key, url in docs.items():

        if not row.get(key):
            row[key] = url

    time.sleep(1.5)  # polite delay


with open(OUTPUT, "w", newline="", encoding="utf-8") as fout:

    writer = csv.DictWriter(fout, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)


print("\n✅ IPO document enrichment complete →", OUTPUT)
