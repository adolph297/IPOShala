import os
import re
import time
import logging
import argparse
from datetime import datetime
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sys

# Add project root to path
sys.path.append(os.getcwd())
from iposhala_test.scripts.mongo import ipo_past_master

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("pipeline_financials.log"), logging.StreamHandler()]
)

BLACKLIST_DOMAINS = ["wikipedia.org", "facebook.com", "twitter.com", "linkedin.com", "youtube.com", "google.com", "meritnation.com", "justdial.com", "indiamart.com", "glassdoor.com", "ambitionbox.com"]
BLACKLIST_KEYWORDS = ["programming", "software", "verilog", "kernel", "linux", "github", "archive", "tutorial", "course", "coding", "algorithm"]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(45)
        return driver
    except Exception as e:
        logging.error(f"Failed to setup driver: {e}")
        return None

def clean_url(url, base_url):
    if not url: return None
    url = url.strip()
    if url.startswith('//'):
        return 'https:' + url
    if url.startswith('/'):
        return urljoin(base_url, url)
    if not url.startswith('http'):
        return urljoin(base_url, url)
    return url

def is_same_domain(url, base_url):
    try:
        url_netloc = urlparse(url).netloc.replace('www.', '').lower()
        base_netloc = urlparse(base_url).netloc.replace('www.', '').lower()
        return url_netloc == base_netloc
    except:
        return False

def is_blacklisted(url, text):
    combined = (url + " " + text).lower()
    if any(d in url.lower() for d in BLACKLIST_DOMAINS):
        return True
    if any(k in combined for k in BLACKLIST_KEYWORDS):
        return True
    return False

def extract_year(text):
    match = re.search(r'(\d{4}[-–—]\d{2,4})|(\d{4})', text)
    return match.group(0) if match else None

def get_companies_to_scan(limit_symbols=None):
    query = {"website": {"$exists": True, "$ne": None}}
    if limit_symbols:
        query["symbol"] = {"$in": limit_symbols}
    return list(ipo_past_master.find(query, {"symbol": 1, "website": 1, "company_name": 1}))

class FinancialCrawler:
    def __init__(self, driver):
        self.driver = driver
        self.found_reports = []
        self.visited_urls = set()
        self.base_domain_url = ""

    def scan_page(self, url, symbol, depth=0):
        if depth > 3 or url in self.visited_urls:
            return
        if is_blacklisted(url, ""):
            return
        if depth > 0 and not is_same_domain(url, self.base_domain_url):
            return
            
        self.visited_urls.add(url)
        try:
            self.driver.get(url)
            time.sleep(5) 
            
            links = self.driver.find_elements(By.TAG_NAME, "a")
            sub_pages = []
            
            if depth == 0:
                common_paths = ["investors", "investor-relations", "financials", "annual-reports", "investor-information"]
                for p in common_paths:
                    sub_pages.append(urljoin(url, p))

            for link in links:
                try:
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    if not href: continue
                    full_url = clean_url(href, url)
                    if not full_url or is_blacklisted(full_url, text): continue

                    is_pdf = ".pdf" in full_url.lower() or ".pdf" in text.lower()
                    keywords = ["annual report", "financial result", "quarterly", "audited", "q1", "q2", "q3", "q4", "half year", "investor presentation"]
                    
                    if any(k in text.lower() for k in keywords) or is_pdf:
                        if is_pdf and (any(k in text.lower() for k in keywords) or re.search(r'\d{4}', text + full_url)):
                            year = extract_year(text) or extract_year(full_url)
                            report = {
                                "desc": text if len(text) > 3 else f"Financial Document ({symbol})",
                                "url": full_url,
                                "year": year,
                                "type": "Annual Report" if "annual" in text.lower() else "Financial Result",
                                "period": "Quarterly" if any(q in text.lower() for q in ["q1","q2","q3","q4"]) else "Other",
                                "source": "pipeline_financials",
                                "scanned_at": datetime.now().isoformat()
                            }
                            self.found_reports.append(report)
                        elif depth < 2:
                            if any(k in text.lower() for k in ["investor", "financial", "report", "compliance", "result"]):
                                if is_same_domain(full_url, self.base_domain_url):
                                    sub_pages.append(full_url)
                except:
                    continue
            for sub_url in list(set(sub_pages)):
                if sub_url not in self.visited_urls:
                    self.scan_page(sub_url, symbol, depth + 1)
        except Exception as e:
            pass 

    def run(self, symbol, website):
        self.found_reports = []
        self.visited_urls = set()
        self.base_domain_url = website
        self.scan_page(website, symbol)
        
        unique = {}
        for r in self.found_reports:
            unique[r['url']] = r
        return list(unique.values())

def process_and_save_reports(symbol, website, reports):
    if not reports:
        return False
        
    annual_reports = []
    financial_results = []
    
    for item in reports:
        label = item.get("desc") or item.get("type")
        doc = {
            "desc": label,
            "url": item.get("url"),
            "source": item.get("source", "pipeline_financials"),
            "imported_at": datetime.now().isoformat()
        }
        if item.get("type") == "Annual Report":
            doc["m_yr"] = item.get("year", "")
            annual_reports.append(doc)
        else:
            doc["period"] = item.get("period", "")
            if item.get("year"):
                doc["year"] = item.get("year")
            financial_results.append(doc)
            
    update_fields = {}
    if annual_reports:
        update_fields["nse_company.annual_reports"] = {
            "__available__": True,
            "data": annual_reports 
        }
    if financial_results:
         update_fields["nse_company.financial_results"] = {
            "__available__": True,
            "data": financial_results
        }
    update_fields["nse_company.extracted_improved"] = reports
    
    if update_fields:
        ipo_past_master.update_one({"symbol": symbol}, {"$set": update_fields})
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Financials Data Pipeline")
    parser.add_argument("--symbols", nargs="+", help="Specific symbols to scan")
    args = parser.parse_args()
    
    companies = get_companies_to_scan(args.symbols)
    logging.info(f"Targeted scan for {len(companies)} symbols.")

    consecutive_errors = 0
    driver = setup_driver()
    
    try:
        for idx, comp in enumerate(companies):
            symbol = comp['symbol']
            website = comp.get('website')
            if not website: continue

            if idx > 0 and idx % 20 == 0:
                logging.info("Periodic driver restart...")
                if driver: driver.quit()
                driver = setup_driver()

            if not driver:
                driver = setup_driver()
                if not driver: break

            logging.info(f"[{idx+1}/{len(companies)}] Processing {symbol}...")
            crawler = FinancialCrawler(driver)
            
            try:
                reports = crawler.run(symbol, website)
                consecutive_errors = 0 
                if reports:
                    logging.info(f"  SUCCESS: Found {len(reports)} reports for {symbol}. Saving to Mongo...")
                    process_and_save_reports(symbol, website, reports)
                else:
                    logging.info(f"  FAILED: No reports found for {symbol}")
            except Exception as e:
                logging.error(f"  Error for {symbol}: {e}")
                consecutive_errors += 1
                try: driver.quit()
                except: pass
                driver = setup_driver()
                if consecutive_errors >= 5:
                    logging.critical("Too many consecutive errors. Exiting.")
                    break
    finally:
        if driver:
            try: driver.quit()
            except: pass

if __name__ == "__main__":
    main()
