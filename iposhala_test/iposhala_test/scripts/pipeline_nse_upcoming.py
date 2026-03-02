import time
import logging
import sys
import os
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.getcwd())
from iposhala_test.scripts.mongo import ipo_live_upcoming
from iposhala_test.scrapers.nse_company_dynamic import fetch_ipo_detail
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_documents(detail_res):
    if not detail_res or not detail_res.get("__available__"): return None, None
    data = detail_res.get("data", {})
    add_details = data.get("additionalDetails", [])
    bid_details = data.get("biddingDetail", [])
    issue_info_list = data.get("issueInfo", {}).get("dataList", [])
    
    all_details = add_details + bid_details + issue_info_list
    docs = {}
    info_updates = {}
    
    mapping = {
        "Red Herring Prospectus": ("docs", "rhp"),
        "Ratios / Basis of Issue Price": ("docs", "ratios"),
        "Bidding Centers": ("docs", "bidding_centers"),
        "Sample Application Forms": ("docs", "forms"),
        "Security Parameters (Pre Anchor)": ("docs", "security_pre"),
        "Security Parameters (Post Anchor)": ("docs", "security_post"),
        "Processing of ASBA Applications": ("info", "asba_circular_pdf"),
        "Video link  for UPI based ASBA process": ("info", "upi_asba_video"),
        "Video link  for BHIM UPI Registration": ("info", "bhim_upi_registration_video")
    }

    for item in all_details:
        title = str(item.get("title", "")).strip()
        val = str(item.get("value", "")).strip()
        if not title or not val or val == "-": continue
        
        url = val
        match = re.search(r"href=([^\s>]+)", val)
        if match:
            url = match.group(1).strip("'\"")
            
        for key, (dest_type, dest_key) in mapping.items():
            if key.lower() in title.lower():
                if dest_type == "docs":
                    docs[dest_key] = url
                elif dest_type == "info":
                    info_updates[dest_key] = url
                break
                
    return docs if docs else None, info_updates if info_updates else None

def fetch_nse_forthcoming():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Prevent detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })

    scraped_symbols = []

    try:
        url = "https://www.nseindia.com/market-data/all-upcoming-issues-ipo"
        logging.info(f"Loading NSE Upcoming IPOs: {url}")
        driver.get(url)
        time.sleep(5)
        
        try:
            tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'UPCOMING ISSUES') or contains(text(), 'Upcoming Issues')]"))
            )
            tab.click()
            time.sleep(3)
        except Exception as e:
            logging.error(f"Failed to click Upcoming Issues tab: {e}")
            return
            
        tables = driver.find_elements(By.TAG_NAME, "table")
        upcoming_table = None
        for t in tables:
            if "upcomingIpoTable" in (t.get_attribute("id") or ""):
                upcoming_table = t
                break
                
        if not upcoming_table:
            logging.error("Could not find upcomingIpoTable on page")
            return
            
        tbodies = upcoming_table.find_elements(By.TAG_NAME, "tbody")
        if not tbodies:
            logging.warning("No tbody found in upcomingIpoTable")
            return
            
        rows = tbodies[0].find_elements(By.TAG_NAME, "tr")
        logging.info(f"Found {len(rows)} Upcoming IPO rows.")
        
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            data = [col.text.strip() for col in cols]
            
            # Expected Data format: 
            # 0: SECURITY TYPE, 1: COMPANY, 2: SYMBOL, 3: ISSUE START DATE, 4: ISSUE END DATE, 
            # 5: STATUS, 6: PRICE RANGE, 7: ISSUE SIZE, 8: DOWNLOAD
            if len(data) >= 8:
                sec_type = data[0]
                company = data[1]
                symbol = data[2]
                start_date = data[3]
                end_date = data[4]
                status_str = data[5]
                price_range = data[6]
                issue_size = data[7]
                
                # Check if it's actually an IPO row
                if not symbol or status_str.lower() not in ["forthcoming", "upcoming"]:
                    continue
                    
                scraped_symbols.append(symbol)
                
                # Fetch Documents
                docs_data = None
                info_updates = None
                try:
                    detail_res = fetch_ipo_detail(symbol)
                    if detail_res and detail_res.get("__available__"):
                        docs_data, info_updates = extract_documents(detail_res)
                except Exception as e:
                    logging.warning(f"Failed to fetch documents for upcoming IPO {symbol}: {e}")
                
                # Insert or update into MongoDB
                ipo_id = f"{symbol.lower()}-{datetime.now().year}"
                
                update_data = {
                    "symbol": symbol,
                    "company_name": company,
                    "status": "UPCOMING",
                    "security_type": "SME" if "sme" in company.lower() else "Equity",
                    "source": "pipeline_nse_upcoming",
                    "last_updated": datetime.now(timezone.utc)
                }
                
                # Combine info
                merged_info = {
                    "issue_start_date": start_date,
                    "issue_end_date": end_date,
                    "issue_price": price_range,
                    "issue_size": issue_size,
                }
                if info_updates:
                    merged_info.update(info_updates)
                    
                update_data["issue_information"] = merged_info
                
                if docs_data:
                    update_data["documents"] = docs_data
                
                # Use symbol as the primary match, but if missing, use company_name
                ipo_live_upcoming.update_one(
                    {"symbol": symbol},
                    {
                        "$set": update_data,
                        "$setOnInsert": {"ipo_id": ipo_id}
                    },
                    upsert=True
                )
                logging.info(f"Updated Upcoming IPO: {company} ({symbol})")

        # Cleanup: Remove IPOs that are stuck in UPCOMING but vanish from the list.
        # This usually means they either moved to LIVE (handled by pipeline_market_data) or got withdrawn.
        if scraped_symbols:
            deleted_res = ipo_live_upcoming.delete_many({
                "source": "pipeline_nse_upcoming",
                "status": "UPCOMING",
                "symbol": {"$nin": scraped_symbols}
            })
            if deleted_res.deleted_count > 0:
                logging.info(f"Cleaned up {deleted_res.deleted_count} stale Upcoming IPOs from DB.")

    except Exception as e:
        logging.error(f"Error scraping NSE Forthcoming: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_nse_forthcoming()
