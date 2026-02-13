import os
import re
import time
import random
from dataclasses import dataclass
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import local

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


# =========================
# LOAD ENV
# =========================
# Modified to load from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "").strip()

# =========================
# CONFIG
# =========================
INPUT_CSV = os.path.join(BASE_DIR, "data", "IPO_bidding_centers_updated.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "company_descriptions.csv")

MAX_WORKERS = 8
TIMEOUT = 20
RETRIES = 2

MIN_WORDS = 15
MAX_WORDS = 170

SERPER_ENDPOINT = "https://google.serper.dev/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

GENERIC_PATTERNS = [
    r"\bshare price\b",
    r"\bhistoric price charts\b",
    r"\bbroker view\b",
    r"\bbuy/sell tips\b",
    r"\bstock price\b",
    r"\bprice charts\b",
]


# =========================
# THREAD SESSION
# =========================
_thread = local()

def get_session():
    if not hasattr(_thread, "session"):
        s = requests.Session()
        s.headers.update(HEADERS)
        _thread.session = s
    return _thread.session


# =========================
# HELPERS
# =========================
def normalize_text(s):
    return re.sub(r"\s+", " ", (s or "").strip())

def truncate_words(text):
    words = (text or "").split()
    if len(words) <= MAX_WORDS:
        return text.strip()
    return " ".join(words[:MAX_WORDS]).strip()

def is_generic(desc):
    d = desc.lower()
    for pat in GENERIC_PATTERNS:
        if re.search(pat, d):
            return True
    return False

def http_get(url):
    session = get_session()
    for _ in range(RETRIES):
        try:
            r = session.get(url, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.text
        except:
            time.sleep(0.4)
    return ""


# =========================
# SERPER SEARCH
# =========================
def serper_search(company_name):
    if not SERPER_API_KEY:
        return []
        
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    query = (
        f'"{company_name}" '
        f'(IPO OR "about company" OR profile OR overview) '
        f'(site:moneycontrol.com OR site:chittorgarh.com OR site:angelone.in)'
    )

    payload = {"q": query, "num": 5}

    try:
        print(f"DEBUG: Searching for {company_name}...")
        r = requests.post(SERPER_ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"DEBUG: Serper Error {r.status_code} - {r.text}")
            return []
        data = r.json()
        results = data.get("organic", [])
        links = [item["link"] for item in results if "link" in item]
        print(f"DEBUG: Found {len(links)} links for {company_name}")
        return links
    except Exception as e:
        print(f"DEBUG: Serper Exception {e}")
        return []


# =========================
# EXTRACT DESCRIPTION
# =========================
def extract_description(html):
    print(f"DEBUG: Extracting from {len(html)} bytes...")
    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"DEBUG: BeautifulSoup Error: {e}")
        return ""

    keywords = [
        "About the Company",
        "Company Profile",
        "Company Information",
        "Business Overview",
        "Overview",
        "Profile",
        "About"
    ]

    # Try section based extraction
    for kw in keywords:
        node = soup.find(string=re.compile(re.escape(kw), re.I))
        if node:
            print(f"DEBUG: Found keyword '{kw}'")
            parent = node.find_parent()
            if parent:
                text = normalize_text(parent.get_text(" ", strip=True))
                print(f"DEBUG: Parent text length: {len(text)}")
                text = truncate_words(text)
                if len(text.split()) >= MIN_WORDS and not is_generic(text):
                    print(f"DEBUG: Selected text from keyword '{kw}'")
                    return text
                else:
                    print(f"DEBUG: Text rejected (Length: {len(text.split())}, Generic: {is_generic(text)})")

    # Fallback paragraphs
    paras = []
    print("DEBUG: Trying fallback paragraphs...")
    for p in soup.find_all("p"):
        t = normalize_text(p.get_text(" ", strip=True))
        if len(t) > 80:
            paras.append(t)

    paras = sorted(set(paras), key=len, reverse=True)
    print(f"DEBUG: Found {len(paras)} candidate paragraphs")
    if paras:
        text = truncate_words(" ".join(paras[:2]))
        if not is_generic(text):
            print("DEBUG: Selected text from paragraphs")
            return text
        else:
            print("DEBUG: Paragraph text rejected as generic")

    return ""


# =========================
# MAIN FETCH
# =========================
def fetch_company(company_name):
    urls = serper_search(company_name)

    for url in urls:
        print(f"DEBUG: Visiting {url}...")
        html = http_get(url)
        if not html:
            continue
        desc = extract_description(html)
        if desc:
            return desc

    return ""


def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Input CSV not found: {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)

    if "COMPANY NAME" not in df.columns:
        raise ValueError("CSV must contain COMPANY NAME column")

    # Deduplicate by COMPANY NAME
    df = df.drop_duplicates(subset=["COMPANY NAME"])
    print(f"Total unique companies: {len(df)}")

    # Check for existing work
    existing = set()
    if os.path.exists(OUTPUT_CSV):
        try:
            existing_df = pd.read_csv(OUTPUT_CSV)
            if "Company Name" in existing_df.columns:
                existing = set(existing_df[existing_df["description"].notna()]["Company Name"])
            print(f"Skipping {len(existing)} companies with existing descriptions.")
        except:
            pass
    
    # Filter df
    target_df = df[~df["COMPANY NAME"].isin(existing)]
    print(f"Processing {len(target_df)} remaining companies...")

    results = [] # In reality this should load existing results if appending, but here we might prefer to just append to file or rewrite.
    # To keep it simple, we will rewrite the file with OLD + NEW results if we want to be safe, 
    # OR just append new results to a file if we use mode='a'.
    # For now, let's just collect all results (including existing?) No, that's complex.
    # Let's just process remaining and APPEND to file.
    
    # We will write header only if file doesn't exist.
    write_header = not os.path.exists(OUTPUT_CSV)
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_company, row["COMPANY NAME"]): row
            for _, row in target_df.iterrows()
        }

        for i, future in enumerate(as_completed(futures)):
            row = futures[future]
            try:
                desc = future.result()
            except Exception as e:
                print(f"DEBUG: Future Exception: {e}")
                desc = ""

            results.append({
                "Symbol": row.get("Symbol", ""),
                "Company Name": row["COMPANY NAME"],
                "description": desc
            })

            if i % 10 == 0:
                print(f"Processed: {i}/{len(df)} - {row['COMPANY NAME']}")

    if results:
        pd.DataFrame(results).to_csv(OUTPUT_CSV, mode='a', header=write_header, index=False, encoding="utf-8")
        print(f"Done. Appended {len(results)} rows to {OUTPUT_CSV}")
    else:
        print("No new descriptions fetched.")


if __name__ == "__main__":
    main()
