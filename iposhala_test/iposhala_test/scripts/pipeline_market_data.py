import os
import sys
import time
import argparse
import requests
import logging
from datetime import datetime, date, timezone, timedelta
from typing import Dict, Any, List

# Add project root to sys.path
sys.path.append(os.getcwd())
from iposhala_test.scripts.mongo import ipo_past_master, ipo_live_upcoming
from iposhala_test.scrapers.nse_company_dynamic import (
    fetch_announcements, fetch_corporate_actions, fetch_annual_reports,
    fetch_brsr_reports, fetch_board_meetings, fetch_event_calendar,
    selenium_fetch_financial_results, selenium_fetch_shareholding_pattern,
    fetch_ipo_detail
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Referer": "https://www.nseindia.com/"}

def parse_subscription(detail_res):
    if not detail_res or not detail_res.get("__available__"): return None
    data = detail_res.get("data", {})
    
    # Check both activeCat (Live) and bidDetails (Past/Closed)
    cat_list = data.get("activeCat", {}).get("dataList", [])
    if not cat_list:
        cat_list = data.get("bidDetails", [])
        
    subs = {"qib": None, "nii": None, "retail": None, "total": None}
    
    for row in cat_list:
        # noOfTotalMeant (activeCat) or noOfTime (bidDetails)
        val = row.get("noOfTotalMeant") or row.get("noOfTime")
        if not val: continue
        try:
            val_float = float(val)
        except ValueError:
            continue
            
        cat = str(row.get("category", "")).lower()
        if "qualified institutional" in cat:
            subs["qib"] = round(val_float, 2)
        elif "non institutional" in cat and row.get("srNo") == "2": # main NII
            subs["nii"] = round(val_float, 2)
        elif "retail individual" in cat:
            subs["retail"] = round(val_float, 2)
        elif "total" in cat:
            subs["total"] = round(val_float, 2)
            
    return subs if any(v is not None for v in subs.values()) else None

import re
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
        
        # Extract href if it's an anchor tag
        url = val
        match = re.search(r"href=([^\s>]+)", val)
        if match:
            url = match.group(1).strip("'\"")
            
        # Match with mapping
        for key, (dest_type, dest_key) in mapping.items():
            if key.lower() in title.lower():
                if dest_type == "docs":
                    docs[dest_key] = url
                elif dest_type == "info":
                    info_updates[dest_key] = url
                break
                
    return docs if docs else None, info_updates if info_updates else None

def fetch_live_ipos():
    urls = [
        "https://www.nseindia.com/api/ipo-current-issue"
    ]
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=HEADERS)
    
    count, today = 0, date.today()
    for url in urls:
        try:
            response = session.get(url, headers=HEADERS)
            response.raise_for_status()
            items = response.json()
            logging.info(f"[LIVE IPOS] Total records received from {url.split('/')[-1]}: {len(items)}")
            
            for item in items:
                try:
                    start_dt = datetime.strptime(item["issueStartDate"], "%d-%b-%Y")
                    end_dt = datetime.strptime(item["issueEndDate"], "%d-%b-%Y")
                except: continue
        
                if today < start_dt.date(): status = "UPCOMING"
                elif start_dt.date() <= today <= end_dt.date(): status = "LIVE"
                elif today > end_dt.date(): status = "CLOSED"
                else: continue

                symbol_str = item.get("symbol", "")
                if not symbol_str: continue
                ipo_id = f"{symbol_str.lower().strip()}-{end_dt.year}"
                
                # Try fetching deeper details for subscription and documents parsing
                subs_data = None
                docs_data = None
                info_updates = None
                
                if status in ["LIVE", "UPCOMING", "CLOSED"]:
                    try:
                        detail_res = fetch_ipo_detail(symbol_str)
                        if detail_res and detail_res.get("__available__"):
                            subs_data = parse_subscription(detail_res)
                            docs_data, info_updates = extract_documents(detail_res)
                    except Exception as loop_e:
                        logging.warning(f"Failed to fetch detail for {symbol_str}: {loop_e}")

                payload = {
                    "symbol": symbol_str,
                    "company_name": item.get("companyName"),
                    "security_type": item.get("marketType"),
                    "issue_start_date": start_dt,
                    "issue_end_date": end_dt,
                    "price_range": item.get("priceBand"),
                    "status": status,
                    "issue_size": item.get("issueSize"),
                    "source": "pipeline_market_data",
                    "last_updated": datetime.now(timezone.utc)
                }
                
                if subs_data:
                    payload["subscription"] = subs_data
                    
                if docs_data:
                    payload["documents"] = docs_data
                    
                if info_updates:
                    payload["issue_information"] = info_updates
                
                ipo_live_upcoming.update_one(
                    {"ipo_id": ipo_id},
                    {"$set": payload},
                    upsert=True
                )
                count += 1
        except Exception as e:
            logging.error(f"[LIVE IPOS] Failed fetching {url}: {e}")
            
    logging.info(f"[LIVE IPOS] Inserted/Updated {count} records")
    
    # Sweep expired IPOs into past master after fetching the latest
    sweep_expired_live_ipos()

def sweep_expired_live_ipos():
    """Finds LIVE/UPCOMING IPOs whose end date has passed, and moves them to PAST MASTER."""
    today = datetime.now(timezone.utc)
    today_naive = datetime.now()
    # Give it a 1-day grace period to ensure timezone safety
    cutoff = today_naive - timedelta(days=1)
    
    all_live = list(ipo_live_upcoming.find())
    expired_ipos = [doc for doc in all_live if isinstance(doc.get("issue_end_date"), datetime) and doc.get("issue_end_date") < cutoff]

    if not expired_ipos:
        return
        
    logging.info(f"[LIVE IPOS] Found {len(expired_ipos)} expired IPOs to transition to CLOSED.")
    migrated = 0
    for doc in expired_ipos:
        symbol = doc.get("symbol")
        if not symbol: continue
        
        doc_issue_info = doc.get("issue_information", {})
        
        # Structure the payload exactly how historical IPOs are structured
        historical_payload = {
            "ipo_id": doc.get("ipo_id"),
            "symbol": symbol,
            "company_name": doc.get("company_name"),
            "security_type": doc.get("security_type", "Equity"),
            "issue_end_date": doc["issue_end_date"].isoformat() if isinstance(doc.get("issue_end_date"), datetime) else doc.get("issue_end_date"),
            "issue_information": {
                "issue_price": doc.get("price_range", "-"),
                "issue_size": doc.get("issue_size", "-"),
                "issue_start_date": doc["issue_start_date"].isoformat() if isinstance(doc.get("issue_start_date"), datetime) else doc.get("issue_start_date"),
                "issue_end_date": doc["issue_end_date"].isoformat() if isinstance(doc.get("issue_end_date"), datetime) else doc.get("issue_end_date"),
                **doc_issue_info # Keep all the video links / circulars
            },
            "status": "CLOSED",
            "source": "live_migration",
            "migrated_at": today
        }
        
        # Bring over subscription data if it exists
        if doc.get("subscription"):
            historical_payload["subscription"] = doc.get("subscription")
            
        if doc.get("documents"):
            historical_payload["documents"] = doc.get("documents")
        
        # Upsert into past master so it appears in the Closed IPOs list
        ipo_past_master.update_one(
            {"ipo_id": doc.get("ipo_id")} if doc.get("ipo_id") else {"symbol": symbol},
            {"$set": historical_payload},
            upsert=True
        )
        
        # Remove from live holding tank
        ipo_live_upcoming.delete_one({"_id": doc["_id"]})
        migrated += 1
        
    logging.info(f"[LIVE IPOS] Successfully migrated {migrated} closed IPOs to historical pool.")


def wrap_section(data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    if not data: return {"available": False, "payload": [], "source_url": None}
    available = data.get("__available__", False)
    raw_data = data.get("data")
    payload = raw_data.get("data", []) if isinstance(raw_data, dict) and "data" in raw_data else (raw_data if isinstance(raw_data, list) else raw_data) if raw_data else []
    
    if isinstance(payload, list):
        payload = [item for item in payload if str(item.get("symbol", "")).upper() == symbol.upper()]
    return {"available": bool(payload), "payload": payload, "source_url": data.get("url")}

def fetch_nse_data(symbol: str, force: bool = False):
    symbol = symbol.upper().strip()
    doc = ipo_past_master.find_one({"symbol": symbol}, {"_id": 1, "nse_company_updated_at": 1})
    if not doc: return False
    
    if not force and doc.get("nse_company_updated_at"):
        if (datetime.now(timezone.utc) - doc.get("nse_company_updated_at").replace(tzinfo=timezone.utc)).days < 7:
            logging.info(f"[NSE DATA] Skipping {symbol} (updated recent 7 days)")
            return True

    logging.info(f"[NSE DATA] Fetching for {symbol}...")
    result, errors = {}, []
    data_sources = [
        ("announcements", fetch_announcements), ("corporate_actions", fetch_corporate_actions),
        ("annual_reports", fetch_annual_reports), ("brsr_reports", fetch_brsr_reports),
        ("board_meetings", fetch_board_meetings), ("event_calendar", fetch_event_calendar),
    ]
    
    for name, func in data_sources:
        try:
            raw = func(symbol)
            result[name] = wrap_section(raw, symbol)
            time.sleep(1)
        except Exception as e:
            errors.append(f"Failed {name}: {str(e)}")
            result[name] = {"available": False, "payload": [], "source_url": None}
            
    payload = {
        "nse_company_updated_at": datetime.now(timezone.utc),
        "nse_company_fetched": True,
        "nse_company_fetch_errors": errors if errors else None
    }
    for k, v in result.items(): payload[f"nse_company.{k}"] = v
    ipo_past_master.update_one({"symbol": symbol}, {"$set": payload})
    return True

def fetch_all_nse_data(limit=None, force=False):
    query = {"$or": [{"nse_company_updated_at": {"$exists": False}}, {"nse_company_updated_at": None}, {"nse_company_updated_at": {"$lt": datetime.now(timezone.utc) - timedelta(days=7)}}]} if not force else {}
    symbols = [d["symbol"] for d in ipo_past_master.find(query, {"symbol": 1}).limit(limit if limit else 0)]
    
    for idx, sym in enumerate(symbols):
        fetch_nse_data(sym, force)
        time.sleep(2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Fetch live upcoming IPOs")
    parser.add_argument("--nse", action="store_true", help="Fetch NSE announcements/corporate data")
    parser.add_argument("--all", action="store_true", help="Run all market data pipelines")
    parser.add_argument("--symbol", type=str, help="Target specific symbol for NSE data")
    parser.add_argument("--limit", type=int, help="Limit batch processing")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.all or args.live: fetch_live_ipos()
    if args.all or args.nse:
        if args.symbol: fetch_nse_data(args.symbol, args.force)
        else: fetch_all_nse_data(args.limit, args.force)
    
    if not any([args.all, args.live, args.nse]):
        parser.print_help()

if __name__ == "__main__":
    main()
