import os
import sys
import re
import requests
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# Add project root to sys.path
sys.path.append(os.getcwd())
try:
    from iposhala_test.scripts.mongo import ipo_past_master, ipo_live_upcoming, ipo_gmp
    from iposhala_test.scrapers.nse_company_dynamic import get_driver
except ImportError:
    # Handle if run from inside scripts directory
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mongo import ipo_past_master, ipo_live_upcoming, ipo_gmp
    from scrapers.nse_company_dynamic import get_driver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def normalize_name(name):
    if not name:
        return ""
    name = name.lower()
    name = re.sub(r'limited', '', name)
    name = re.sub(r'ltd', '', name)
    name = re.sub(r'ipo', '', name)
    name = re.sub(r'[^a-z0-9]', '', name)
    return name.strip()

def parse_num(s):
    if not s:
        return 0
    s_cleaned = re.sub(r'[^0-9.-]+', '', s)
    try:
        return float(s_cleaned) if s_cleaned else 0
    except ValueError:
        return 0

def fetch_and_store_gmp():
    logging.info("Fetching live GMP data...")
    url = "https://www.investorgain.com/report/ipo-gmp-performance/377/"
    driver = None
    
    try:
        driver = get_driver(headless=True)
        driver.get(url)
        time.sleep(5)  # Wait for table to load
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        scraped_data = []
        
        # Investorgain's GMP table usually has the class 'table-bordered' or '#mainTable'
        for row in soup.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) < 5:
                continue
            
            company_name = tds[0].get_text(strip=True)
            if not company_name or "Company" in company_name:
                continue
                
            scraped_data.append({
                "companyName": company_name,
                "issuePrice": parse_num(tds[1].get_text(strip=True)),
                "gmp": parse_num(tds[2].get_text(strip=True)),
                "estimatedListingPrice": parse_num(tds[3].get_text(strip=True)),
                "expectedGainPercent": parse_num(tds[4].get_text(strip=True))
            })
            
        logging.info(f"Scraped {len(scraped_data)} rows from GMP table.")

        # Fetch IPOs from DB to match
        live_ipos = list(ipo_live_upcoming.find({}, {"_id": 0, "ipo_id": 1, "symbol": 1, "company_name": 1, "status": 1}))
        past_ipos = list(ipo_past_master.find({}, {"_id": 0, "ipo_id": 1, "symbol": 1, "company_name": 1, "status": 1}))
        all_ipos = live_ipos + past_ipos

        matched_data = []
        for scraped in scraped_data:
            normalized_scraped = normalize_name(scraped["companyName"])
            
            matched_ipo = next((ipo for ipo in all_ipos if 
                              normalize_name(ipo.get("company_name", "")) == normalized_scraped or 
                              normalized_scraped in normalize_name(ipo.get("company_name", "")) or
                              normalize_name(ipo.get("company_name", "")) in normalized_scraped), None)

            if matched_ipo:
                ipo_id = matched_ipo.get("ipo_id") or matched_ipo.get("symbol")
                if ipo_id:
                    matched_data.append({
                        "ipo_id": ipo_id,
                        "companyName": scraped["companyName"],
                        "issuePrice": scraped["issuePrice"],
                        "gmp": scraped["gmp"],
                        "estimatedListingPrice": scraped["estimatedListingPrice"],
                        "expectedGainPercent": scraped["expectedGainPercent"],
                        "lastUpdated": datetime.now(timezone.utc)
                    })

        # Upsert matched data into GMP collection
        for data in matched_data:
            ipo_gmp.update_one(
                {"ipo_id": data["ipo_id"]},
                {"$set": data},
                upsert=True
            )

        logging.info(f"Successfully updated {len(matched_data)} GMP records.")
        return matched_data

    except Exception as e:
        logging.error(f"Error in GMP Scraper: {e}")
        raise e
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    fetch_and_store_gmp()
