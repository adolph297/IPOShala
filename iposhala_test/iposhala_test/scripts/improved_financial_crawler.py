
import os
import re
import json
import time
import random
import logging
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from iposhala_test.scripts.mongo import ipo_past_master

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("improved_crawler.log"), logging.StreamHandler()]
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
        driver.set_page_load_timeout(45) # Increased timeout
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

def get_companies_to_scan(category=None):
    if category == "failure":
        try:
            with open('extraction_categories.json', 'r') as f:
                cats = json.load(f)
                symbols = [s.split('(')[-1].rstrip(')') for s in cats.get('crawler_failure', [])]
                return list(ipo_past_master.find({"symbol": {"$in": symbols}}, {"symbol": 1, "website": 1, "company_name": 1}))
        except:
            pass
    
    return list(ipo_past_master.find({
        "website": {"$exists": True, "$ne": None},
        "nse_company.financial_results": {"$exists": False}
    }, {"symbol": 1, "website": 1, "company_name": 1}))

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
                                "source": "selenium_v2",
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
            raise e 

    def run(self, symbol, website):
        self.found_reports = []
        self.visited_urls = set()
        self.base_domain_url = website
        self.scan_page(website, symbol)
        
        unique = {}
        for r in self.found_reports:
            unique[r['url']] = r
        return list(unique.values())

def main():
    limit_symbols = sys.argv[1:] if len(sys.argv) > 1 else None
    
    companies = get_companies_to_scan(category="failure")
    if limit_symbols:
        companies = [c for c in companies if c['symbol'] in limit_symbols]
        logging.info(f"Targeted scan for {len(companies)} symbols.")
    
    results_file = 'batch_6_improved_financials.json'
    all_data = {}
    if os.path.exists(results_file):
        try:
            with open(results_file, 'r') as f:
                all_data = json.load(f)
        except:
            logging.warning("Existing results file corruped, starting fresh.")

    consecutive_errors = 0
    driver = setup_driver()
    
    try:
        for idx, comp in enumerate(companies):
            symbol = comp['symbol']
            website = comp.get('website')
            
            if not website: continue

            # Skip Logic: Only skip if we already have SUCCESSFUL audited_financials
            if not limit_symbols and symbol in all_data and all_data[symbol].get('audited_financials'):
                continue
            
            # PROTECT EXISTING SUCCESSES
            existing_success = all_data.get(symbol, {}).get('audited_financials')

            # Periodic Restart to avoid memory leaks / port exhaustion
            if idx > 0 and idx % 20 == 0:
                logging.info("Periodic driver restart...")
                if driver: driver.quit()
                driver = setup_driver()

            if not driver:
                logging.error(f"  Driver missing for {symbol}. Re-setting...")
                driver = setup_driver()
                if not driver:
                    break

            logging.info(f"[{idx+1}/{len(companies)}] Processing {symbol}...")
            crawler = FinancialCrawler(driver)
            
            try:
                reports = crawler.run(symbol, website)
                consecutive_errors = 0 
                
                if reports:
                    logging.info(f"  SUCCESS: Found {len(reports)} reports for {symbol}")
                    all_data[symbol] = {
                        "website": website,
                        "audited_financials": reports,
                        "improved_scan": True,
                        "last_scanned": datetime.now().isoformat()
                    }
                else:
                    logging.info(f"  FAILED: No reports found for {symbol}")
                    if not existing_success:
                        all_data[symbol] = {"website": website, "found": False, "last_scanned": datetime.now().isoformat()}

                with open(results_file, 'w') as f:
                    json.dump(all_data, f, indent=2)
                    
            except Exception as e:
                logging.error(f"  Error for {symbol}: {e}")
                consecutive_errors += 1
                
                # If driver crashed, try to recreate once
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
        with open(results_file, 'w') as f:
            json.dump(all_data, f, indent=2)

if __name__ == "__main__":
    main()
