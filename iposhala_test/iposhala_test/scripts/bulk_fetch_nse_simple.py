"""
Bulk NSE Data Fetcher (No Selenium)

Fetches NSE company data for all IPOs using plain requests library.
This version avoids Selenium/ChromeDriver issues.

Usage:
    python bulk_fetch_nse_simple.py --limit 10
    python bulk_fetch_nse_simple.py --all
"""

import os
import sys
import time
import argparse
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import requests

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iposhala_test.scripts.mongo import ipo_past_master

# Configuration
DELAY_BETWEEN_SYMBOLS = 0.3  # seconds (minimum for stability)
DELAY_BETWEEN_REQUESTS = 0.1  # seconds (minimum for stability)
SKIP_RECENT_DAYS = 7

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nseindia.com/",
}


def log(message: str, level: str = "INFO"):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def create_session(symbol=None):
    """Create a requests session with NSE cookies"""
    s = requests.Session()
    try:
        # Simple warmup
        s.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)
        time.sleep(1)
        return s
    except Exception as e:
        log(f"Failed to create session: {e}", "ERROR")
        return None


def fetch_nse_data(session: requests.Session, url: str, symbol: str) -> Dict[str, Any]:
    """
    Fetch data from NSE API
    Returns: {available: bool, payload: list/dict, source_url: str}
    """
    try:
        res = session.get(url, headers=NSE_HEADERS, timeout=20)
        
        if res.status_code == 404:
            return {"available": False, "payload": [], "source_url": url}
        
        if res.status_code == 401 or res.status_code == 403:
            log(f"  Auth Error {res.status_code} for {url}. Refreshing session...", "WARNING")
            # Side effect: we don't return here, we let it fail or retry in caller
            return {"available": False, "payload": [], "source_url": url}
            
        if res.status_code != 200:
            log(f"  HTTP {res.status_code} for {url}", "WARNING")
            return {"available": False, "payload": [], "source_url": url}
        
        # Check content type
        ct = (res.headers.get("content-type") or "").lower()
        if "application/json" not in ct:
            log(f"  Non-JSON response for {url}", "WARNING")
            # debug raw
            # log(f"  RAW: {res.text[:100]}", "DEBUG")
            return {"available": False, "payload": [], "source_url": url}
        
        try:
            data = res.json()
        except Exception as e:
            log(f"  JSON decode error for {url}: {e}", "ERROR")
            # log(f"  RAW: {res.text[:100]}", "DEBUG")
            return {"available": False, "payload": [], "source_url": url}
        
        # Extract payload
        payload = []
        if isinstance(data, dict) and "data" in data:
            payload = data.get("data", [])
        elif isinstance(data, list):
            payload = data
        elif isinstance(data, dict):
            # Some endpoints return dict directly (financial_results, shareholding_pattern)
            return {"available": bool(data), "payload": data, "source_url": url}
        
        # Filter by symbol for list payloads
        if isinstance(payload, list):
            # For announcements, sometimes symbol is in 'symbol' or 'Symbol'
            payload = [
                item for item in payload 
                if (item.get("symbol", "") or item.get("Symbol", "") or "").upper() == symbol.upper()
            ]
        
        return {
            "available": bool(payload),
            "payload": payload,
            "source_url": url
        }
        
    except Exception as e:
        log(f"  Error fetching {url}: {e}", "ERROR")
        return {"available": False, "payload": [], "source_url": url}


def fetch_with_index_fallback(session: requests.Session, symbol: str, endpoint: str) -> Dict[str, Any]:
    """Try fetching from multiple indexes (equities, sme, debt)"""
    indexes = ["equities", "sme", "debt"]
    
    for idx in indexes:
        url = f"https://www.nseindia.com/api/{endpoint}?index={idx}&symbol={symbol}"
        result = fetch_nse_data(session, url, symbol)
        
        if result["available"]:
            return result
        
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Return last attempt result
    return result


def fetch_all_data_for_symbol(session: requests.Session, symbol: str) -> Dict[str, Any]:
    """Fetch all NSE company data for a given symbol"""
    log(f"Fetching NSE data for {symbol}...", "INFO")
    result = {}
    errors = []
    
    # Define all data sources
    data_sources = [
        ("announcements", "corporate-announcements"),
        ("corporate_actions", "corporates-corporate-actions"),
        ("annual_reports", "annual-reports"),
        ("brsr_reports", "brsr-reports"),
        ("board_meetings", "corporates-board-meetings"),
        ("financial_results", "corporates-financial-results"),
        ("shareholding_pattern", "corporates-share-holding-pattern"),
    ]
    
    for section_name, endpoint in data_sources:
        try:
            log(f"  Fetching {section_name}...", "DEBUG")
            data = fetch_with_index_fallback(session, symbol, endpoint)
            result[section_name] = data
            
            # Log count
            if isinstance(data.get("payload"), list):
                count = len(data["payload"])
                log(f"    + {section_name}: {count} items", "DEBUG")
            elif data.get("available"):
                log(f"    + {section_name}: available", "DEBUG")
            else:
                log(f"    - {section_name}: not available", "DEBUG")
                
        except Exception as e:
            error_msg = f"Failed to fetch {section_name}: {str(e)}"
            log(f"    - {error_msg}", "ERROR")
            errors.append(error_msg)
            result[section_name] = {"available": False, "payload": [], "source_url": None}
    
    # Event calendar (no index parameter)
    try:
        log(f"  Fetching event_calendar...", "DEBUG")
        url = f"https://www.nseindia.com/api/event-calendar?symbol={symbol}"
        data = fetch_nse_data(session, url, symbol)
        result["event_calendar"] = data
        
        if isinstance(data.get("payload"), list):
            log(f"    + event_calendar: {len(data['payload'])} items", "DEBUG")
        elif data.get("available"):
            log(f"    + event_calendar: available", "DEBUG")
        else:
            log(f"    - event_calendar: not available", "DEBUG")
    except Exception as e:
        errors.append(f"Failed to fetch event_calendar: {str(e)}")
        result["event_calendar"] = {"available": False, "payload": [], "source_url": None}
    
    return result, errors


def populate_single_symbol(session: requests.Session, symbol: str, force: bool = False) -> bool:
    """Fetch and update NSE data for a single symbol"""
    symbol = symbol.upper().strip()
    
    # Check if symbol exists
    doc = ipo_past_master.find_one({"symbol": symbol}, {"_id": 1, "nse_company_updated_at": 1})
    if not doc:
        log(f"Symbol {symbol} not found in database", "ERROR")
        return False
    
    # Check if recently updated (unless force)
    if not force:
        updated_at = doc.get("nse_company_updated_at")
        if updated_at:
            # Handle both timezone-aware and timezone-naive datetimes
            if updated_at.tzinfo is None:
                # Make it timezone-aware (assume UTC)
                updated_at = updated_at.replace(tzinfo=timezone.utc)
            
            age = datetime.now(timezone.utc) - updated_at
            if age.days < SKIP_RECENT_DAYS:
                log(f"Skipping {symbol} (updated {age.days} days ago)", "INFO")
                return True
    
    # Fetch all data
    try:
        nse_data, errors = fetch_all_data_for_symbol(session, symbol)
        
        # Prepare update payload
        update_payload = {
            "nse_company_updated_at": datetime.now(timezone.utc),
            "nse_company_fetched": True,
            "nse_company_fetch_errors": errors if errors else None
        }
        
        # Add each section to update payload
        for section_name, section_data in nse_data.items():
            update_payload[f"nse_company.{section_name}"] = section_data
        
        # Update MongoDB
        result = ipo_past_master.update_one(
            {"symbol": symbol},
            {"$set": update_payload}
        )
        
        if result.modified_count > 0:
            log(f"Successfully updated {symbol}", "SUCCESS")
            return True
        else:
            log(f"No changes for {symbol} (data may be identical)", "WARNING")
            return True
            
    except Exception as e:
        log(f"Failed to update {symbol}: {str(e)}", "ERROR")
        return False


def populate_all_symbols(limit: int = None, offset: int = 0, skip_recent: bool = True):
    """Fetch and update NSE data for all symbols in database"""
    # Initial session
    session = create_session()
    if not session:
        log("Failed to create NSE session", "ERROR")
        return
    
    # Get all symbols
    query = {}
    if skip_recent:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=SKIP_RECENT_DAYS)
        query = {
            "$or": [
                {"nse_company_updated_at": {"$exists": False}},
                {"nse_company_updated_at": None},
                {"nse_company_updated_at": {"$lt": cutoff_date}}
            ]
        }
    
    cursor = ipo_past_master.find(query, {"symbol": 1}).skip(offset)
    if limit:
        cursor = cursor.limit(limit)
    
    symbols = [doc["symbol"] for doc in cursor]
    total = len(symbols)
    
    log(f"Found {total} symbols to process (offset={offset}, limit={limit})", "INFO")
    
    if total == 0:
        log("No symbols to process", "INFO")
        return
    
    # Process each symbol
    success_count = 0
    failure_count = 0
    start_time = time.time()
    
    for idx, symbol in enumerate(symbols, 1):
        log(f"\n{'='*60}", "INFO")
        log(f"Processing {idx}/{total}: {symbol}", "INFO")
        log(f"{'='*60}", "INFO")
        
        # Per-symbol session for better cookie handling
        if idx % 10 == 0:  # Refresh every 10 symbols OR if it's a critical one
            session = create_session(symbol)
            
        success = populate_single_symbol(session, symbol, force=not skip_recent)
        
        if success:
            success_count += 1
        else:
            failure_count += 1
        
        # Progress update
        elapsed = time.time() - start_time
        avg_time = elapsed / idx
        remaining = (total - idx) * avg_time
        eta = datetime.now() + timedelta(seconds=remaining)
        
        log(f"\nProgress: {idx}/{total} ({idx/total*100:.1f}%)", "INFO")
        log(f"Success: {success_count}, Failures: {failure_count}", "INFO")
        log(f"Elapsed: {elapsed/60:.1f}m, ETA: {eta.strftime('%H:%M:%S')}", "INFO")
        
        # Delay between symbols (except last one)
        if idx < total:
            log(f"Waiting {DELAY_BETWEEN_SYMBOLS}s before next symbol...\n", "INFO")
            time.sleep(DELAY_BETWEEN_SYMBOLS)
        
        # Refresh session every 50 symbols
        if idx % 50 == 0:
            log("Refreshing session...", "INFO")
            session = create_session()
            if not session:
                log("Failed to refresh session, continuing with old session", "WARNING")
    
    # Final summary
    total_time = time.time() - start_time
    log(f"\n{'='*60}", "INFO")
    log(f"COMPLETED", "SUCCESS")
    log(f"{'='*60}", "INFO")
    log(f"Total processed: {total}", "INFO")
    log(f"Successful: {success_count}", "SUCCESS")
    log(f"Failed: {failure_count}", "ERROR")
    log(f"Total time: {total_time/60:.1f} minutes", "INFO")
    log(f"Average time per symbol: {total_time/total:.1f}s", "INFO")


def main():
    parser = argparse.ArgumentParser(description="Fetch NSE company data for IPOs (No Selenium)")
    parser.add_argument("--symbol", type=str, help="Fetch data for specific symbol")
    parser.add_argument("--all", action="store_true", help="Fetch data for all symbols")
    parser.add_argument("--limit", type=int, help="Limit number of symbols to process")
    parser.add_argument("--offset", type=int, default=0, help="Offset for batch processing")
    parser.add_argument("--skip-recent", action="store_true", default=True, 
                       help=f"Skip symbols updated within last {SKIP_RECENT_DAYS} days")
    parser.add_argument("--force", action="store_true", help="Force update even if recently updated")
    
    args = parser.parse_args()
    
    if args.symbol:
        # Single symbol mode
        session = create_session(args.symbol)
        if session:
            populate_single_symbol(session, args.symbol, force=args.force)
    elif args.all or args.limit:
        # Batch mode
        populate_all_symbols(
            limit=args.limit,
            offset=args.offset,
            skip_recent=args.skip_recent and not args.force
        )
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python bulk_fetch_nse_simple.py --symbol RELIANCE")
        print("  python bulk_fetch_nse_simple.py --limit 10")
        print("  python bulk_fetch_nse_simple.py --all --skip-recent")


if __name__ == "__main__":
    main()
