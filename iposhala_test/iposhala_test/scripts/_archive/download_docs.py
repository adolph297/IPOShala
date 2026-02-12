import csv
import os
import requests
from urllib.parse import urlparse

INPUT = "data/IPO_transform_.csv"
OUTPUT_DIR = "downloads"

DOC_COLUMNS = [
    "doc_anchor",
    "doc_rhp",
    "doc_bidding",
    "doc_sample",
    "doc_security_pre",
    "doc_security_post",
    "doc_anchor_report",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

def safe_name(name):
    return "".join(c for c in name if c.isalnum() or c in " _-").strip()

def download_file(url, folder):
    try:
        filename = os.path.basename(urlparse(url).path)
        path = os.path.join(folder, filename)

        r = requests.get(url, headers=HEADERS, timeout=30)

        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            print("   ✔", filename)
        else:
            print("   ✖ Failed:", url)

    except Exception as e:
        print("   ERROR:", e)

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        company = safe_name(row.get("COMPANY NAME", "IPO"))
        folder = os.path.join(OUTPUT_DIR, company)
        os.makedirs(folder, exist_ok=True)

        print(f"\nDownloading for {company}")

        for col in DOC_COLUMNS:
            url = row.get(col)

            if url and url.startswith("http"):
                download_file(url, folder)

print("\n✅ All downloads complete")
