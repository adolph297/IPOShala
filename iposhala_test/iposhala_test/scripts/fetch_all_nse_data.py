"""
Comprehensive NSE Data Fetcher for All IPOs

This script fetches all available NSE company data for IPOs in the database:
- Announcements
- Corporate Actions
- Annual Reports
- BRSR Reports
- Board Meetings
- Event Calendar
- Financial Results
- Shareholding Pattern

Usage:
    # Fetch for single symbol
    python fetch_all_nse_data.py --symbol RELIANCE
    
    # Fetch for all symbols (skip recent updates)
    python fetch_all_nse_data.py --all --skip-recent
    
    # Fetch for specific batch
    python fetch_all_nse_data.py --limit 20 --offset 0
"""

import os
import sys
import time
import argparse
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iposhala_test.scripts.mongo import ipo_past_master
from iposhala_test.scrapers.nse_company_dynamic import (
    fetch_announcements,
    fetch_annual_reports,
    fetch_brsr_reports,
    fetch_board_meetings,
    fetch_event_calendar,
    fetch_corporate_actions,
    selenium_fetch_financial_results,
    selenium_fetch_shareholding_pattern
)


# Configuration
DELAY_BETWEEN_SYMBOLS = 3  # seconds
DELAY_BETWEEN_REQUESTS = 1  # seconds
SKIP_RECENT_DAYS = 7  # Skip symbols updated within this many days


def log(message: str, level: str = "INFO"):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def wrap_section(data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    """
    Wrap NSE API response into standardized format
    Returns: {available: bool, payload: list, source_url: str}
    """
    if not data:
        return {"available": False, "payload": [], "source_url": None}
    
    available = data.get("__available__", False)
    raw_data = data.get("data")
    source_url = data.get("url")
    
    # Extract payload
    payload = []
    if available and raw_data:
        if isinstance(raw_data, dict) and "data" in raw_data:
            payload = raw_data.get("data", [])
        elif isinstance(raw_data, list):
            payload = raw_data
        elif isinstance(raw_data, dict):
            # Some endpoints return dict directly
            payload = raw_data
    
    # Filter by symbol for list payloads
    if isinstance(payload, list):
        payload = [
            item for item in payload 
            if (item.get("symbol", "") or "").upper() == symbol.upper()
        ]
    
    return {
        "available": bool(payload) if isinstance(payload, list) else bool(payload),
        "payload": payload,
        "source_url": source_url
    }


def fetch_all_data_for_symbol(symbol: str) -> Dict[str, Any]:
    """
    Fetch all NSE company data for a given symbol
    Returns dict with all sections
    """
    log(f"Fetching NSE data for {symbol}...", "INFO")
    result = {}
    errors = []
    
    # Define all data sources
    data_sources = [
        ("announcements", fetch_announcements),
        ("corporate_actions", fetch_corporate_actions),
        ("annual_reports", fetch_annual_reports),
        ("brsr_reports", fetch_brsr_reports),
        ("board_meetings", fetch_board_meetings),
        ("event_calendar", fetch_event_calendar),
        ("financial_results", selenium_fetch_financial_results),
        ("shareholding_pattern", selenium_fetch_shareholding_pattern),
    ]
    
    for section_name, fetch_func in data_sources:
        try:
            log(f"  Fetching {section_name}...", "DEBUG")
            raw_data = fetch_func(symbol)
            
            # Wrap the data
            if section_name in ["financial_results", "shareholding_pattern"]:
                # These return dict directly, not list
                result[section_name] = raw_data.get("data") if raw_data.get("__available__") else None
            else:
                # These return lists
                wrapped = wrap_section(raw_data, symbol)
                result[section_name] = wrapped
                
                # Log count
                if isinstance(wrapped.get("payload"), list):
                    count = len(wrapped["payload"])
                    log(f"    ✓ {section_name}: {count} items", "DEBUG")
                else:
                    log(f"    ✓ {section_name}: available", "DEBUG")
            
            # Rate limiting between requests
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
        except Exception as e:
            error_msg = f"Failed to fetch {section_name}: {str(e)}"
            log(f"    ✗ {error_msg}", "ERROR")
            errors.append(error_msg)
            result[section_name] = {"available": False, "payload": [], "source_url": None}
    
    return result, errors


def populate_single_symbol(symbol: str, force: bool = False) -> bool:
    """
    Fetch and update NSE data for a single symbol
    Returns True if successful, False otherwise
    """
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
            age = datetime.now(timezone.utc) - updated_at
            if age.days < SKIP_RECENT_DAYS:
                log(f"Skipping {symbol} (updated {age.days} days ago)", "INFO")
                return True
    
    # Fetch all data
    try:
        nse_data, errors = fetch_all_data_for_symbol(symbol)
        
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
            log(f"✅ Successfully updated {symbol}", "SUCCESS")
            return True
        else:
            log(f"⚠️  No changes for {symbol} (data may be identical)", "WARNING")
            return True
            
    except Exception as e:
        log(f"❌ Failed to update {symbol}: {str(e)}", "ERROR")
        return False


def populate_all_symbols(limit: int = None, offset: int = 0, skip_recent: bool = True):
    """
    Fetch and update NSE data for all symbols in database
    """
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
        
        success = populate_single_symbol(symbol, force=not skip_recent)
        
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
    parser = argparse.ArgumentParser(description="Fetch NSE company data for IPOs")
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
        populate_single_symbol(args.symbol, force=args.force)
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
        print("  python fetch_all_nse_data.py --symbol RELIANCE")
        print("  python fetch_all_nse_data.py --all --skip-recent")
        print("  python fetch_all_nse_data.py --limit 20 --offset 0")


if __name__ == "__main__":
    main()
