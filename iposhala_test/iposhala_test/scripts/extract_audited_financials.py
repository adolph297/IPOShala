import requests
from bs4 import BeautifulSoup
import re
import argparse
import urllib3
from iposhala_test.scripts.mongo import ipo_past_master
from datetime import datetime, timezone

# Disable insecure request warnings for verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

# Known website mappings for test cases (if missing from DB)
WEBSITE_MAP = {
    "ADVANCE": "https://advanceagrolife.com/",
    "GKSL": "https://www.gujaratsuperspecialityhospital.com/",
    "GLOTTIS": "https://glottislogistics.in/",
    "OMFREIGHT": "https://omfreight.com/",
    "JKIPL": "https://www.jkipl.in/",
    "PACEDIGITK": "https://www.pacedigitek.com/"
}

def resolve_company(symbol):
    # Prioritize WEBSITE_MAP for manual/test overrides
    website = WEBSITE_MAP.get(symbol)
    
    doc = ipo_past_master.find_one({"symbol": symbol})
    if not doc:
        return None, website
    
    name = doc.get("company_name") or doc.get("nse_quote", {}).get("info", {}).get("companyName")
    if not website:
        website = doc.get("website") or doc.get("company_website")
    
    return name, website

def get_base_url(url):
    parts = url.split("/")
    return "/".join(parts[:3])

def extract_audited_financials(symbol):
    name, website = resolve_company(symbol)
    if not website:
        print(f"Error: Website not found for {symbol} ({name})")
        return

    print(f"Target: {symbol} | Company: {name} | Website: {website}")
    
    # Discovery Phase: Find the Investor/Reports page
    discovery_urls = [website.rstrip('/') + "/"]
    
    # Add common paths
    common_paths = [
        "investors", "investor-relations", "financial-information", 
        "annual-reports", "web/annual_reports", "web/investors",
        "investor-information"
    ]
    for p in common_paths:
        discovery_urls.append(website.rstrip('/') + "/" + p)

    found_reports = []
    checked_urls = set()

    for url in discovery_urls:
        if url in checked_urls: continue
        checked_urls.add(url)
        
        print(f"Scanning {url}...")
        try:
            res = requests.get(url, headers=HEADERS, timeout=15, verify=False)
            if res.status_code != 200:
                if res.status_code != 404:
                    print(f"  Warning: Received status {res.status_code} for {url}")
                continue
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 1. Crawl for sub-links if we are on the main page
            if url == discovery_urls[0]:
                links = soup.find_all('a', href=True)
                print(f"  Found {len(links)} links on {url}")
                for l in links:
                    ltext = l.get_text().lower()
                    lhref = l['href']
                    if any(k in ltext for k in ["investor", "annual", "report", "financial"]):
                        if not lhref.startswith('http'):
                            lhref = get_base_url(website) + "/" + lhref.lstrip('/')
                        if lhref not in checked_urls:
                            print(f"    Found potential sub-page: {ltext} -> {lhref}")
                            discovery_urls.append(lhref)

            # 2. Extract PDFs from current page
            # Method A: Direct link text
            plinks = soup.find_all('a', href=True)
            for l in plinks:
                ltext = l.get_text().strip()
                lhref = l['href']
                
                if "Annual Report" in ltext or "Audited" in ltext:
                    print(f"    Checking candidate link: {ltext} -> {lhref}")
                    year_match = re.search(r'(\d{4}-\d{2,4})', ltext)
                    if year_match and (".pdf" in lhref.lower() or "pdf" in ltext.lower() or "View" in ltext):
                        year = year_match.group(1)
                        full_url = lhref
                        if not full_url.startswith('http'):
                            full_url = get_base_url(url) + "/" + full_url.lstrip('/')
                        
                        print(f"    [Method A] Found report: {year} -> {full_url}")
                        found_reports.append({
                            "year": year,
                            "url": full_url,
                            "type": "Annual Report",
                            "period": "Annual"
                        })

            # Method B: Sibling structure
            all_text_nodes = soup.find_all(string=re.compile(r'Annual Report', re.I))
            for node in all_text_nodes:
                parent = node.parent
                container = parent
                for _ in range(3):
                    link = container.find('a', href=True) if container else None
                    if link and ".pdf" in link['href'].lower():
                        ltext = node.strip()
                        lhref = link['href']
                        year_match = re.search(r'(\d{4}[-–—]\d{2,4})', ltext)
                        if year_match:
                            year = year_match.group(1)
                            full_url = lhref
                            if not full_url.startswith('http'):
                                full_url = get_base_url(url) + "/" + full_url.lstrip('/')
                            
                            print(f"    [Method B] Found report: {year} -> {full_url}")
                            found_reports.append({
                                "year": year,
                                "url": full_url,
                                "type": "Annual Report",
                                "period": "Annual"
                            })
                            break
                    container = container.parent if container else None
                    if not container: break

        except Exception as e:
            print(f"  Error: {e}")

    # Deduplicate and update
    if found_reports:
        unique_reports = {}
        for r in found_reports:
            # Normalize year 2023-24
            unique_reports[r["year"]] = r
        
        final_list = sorted(unique_reports.values(), key=lambda x: x["year"], reverse=True)
        print(f"\nFound {len(final_list)} unique reports for {symbol}")
        
        ipo_past_master.update_one(
            {"symbol": symbol},
            {
                "$set": {
                    "nse_company.audited_financials": final_list,
                    "last_discovery_audited": datetime.now(timezone.utc)
                }
            }
        )
        print("MongoDB updated successful.")
    else:
        print(f"No reports found for {symbol}")

import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", help="Company symbol (e.g. ADVANCE). If omitted, scans all.")
    args = parser.parse_args()
    
    if args.symbol:
        extract_audited_financials(args.symbol.upper())
    else:
        print("Starting full scan of all IPOs...")
        cursor = ipo_past_master.find({}, {"symbol": 1})
        symbols = [doc['symbol'] for doc in cursor if doc.get('symbol')]
        print(f"Total companies to scan: {len(symbols)}")
        for idx, symbol in enumerate(symbols):
            print(f"[{idx+1}/{len(symbols)}] Processing {symbol}...")
            try:
                extract_audited_financials(symbol)
                # Small sleep to be polite
                time.sleep(0.5)
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
