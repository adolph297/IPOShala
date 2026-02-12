from datetime import datetime
import time
import requests

from iposhala_test.scripts.mongo import ipo_past_master  # same collection used in ingest


NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}


def get_session():
    s = requests.Session()
    # Warmup NSE cookies
    s.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)
    return s


def fetch_quote(symbol: str, session: requests.Session, retries: int = 3):
    """
    NSE blocks / fails randomly. Retry a few times.
    Checks both Equity and SME endpoints for the symbol.
    """
    symbol = symbol.upper().strip()
    
    # Try Equity first, then SME
    endpoints = [
        f"https://www.nseindia.com/api/quote-equity?symbol={symbol}",
        f"https://www.nseindia.com/api/quote-sme?symbol={symbol}"
    ]
    
    last_err = None
    for api_url in endpoints:
        for attempt in range(1, retries + 1):
            try:
                res = session.get(api_url, headers=NSE_HEADERS, timeout=10)
                
                if res.status_code == 200:
                    return res.json()
                
                if res.status_code == 404:
                    # Not in this index, break inner loop to try next endpoint
                    last_err = f"NSE status=404 for {api_url}"
                    break
                
                # If blocked, NSE often gives 401/403
                last_err = f"NSE status={res.status_code}, body={res.text[:200]}"
                time.sleep(1 * attempt)
                
            except Exception as e:
                last_err = str(e)
                time.sleep(1 * attempt)
                
    raise Exception(f"Symbol {symbol} not found in any index or blocked: {last_err}")


def extract_sections(json_data: dict):
    """
    Extract everything needed for NSE-like page:
    - price info
    - security info
    - trade info
    - order book depth
    Plus: ISIN (needed for announcements, annual reports etc.)
    """
    market_dept = json_data.get("marketDeptOrderBook", {}) or {}

    # ISIN location varies; metadata.isin is common
    isin = None
    metadata = json_data.get("metadata", {}) or {}
    if isinstance(metadata, dict):
        isin = metadata.get("isin")

    return {
        "isin": isin,
        "price_info": json_data.get("priceInfo", {}) or {},
        "security_info": json_data.get("securityInfo", {}) or {},
        "trade_info": market_dept.get("tradeInfo", {}) or {},
        "order_book": {
            "bids": market_dept.get("bid", []) or [],
            "asks": market_dept.get("ask", []) or [],
        },
        # helpful fields for debug and future modules
        "metadata": metadata if isinstance(metadata, dict) else {},
        "info": json_data.get("info", {}) if isinstance(json_data.get("info", {}), dict) else {}
    }


def main(limit=25, sleep_seconds=1):
    print(">>> FETCHING NSE QUOTE DATA INTO MONGODB <<<")

    session = get_session()

    cursor = ipo_past_master.find(
        {"symbol": {"$ne": None}, "nse_quote_fetched": {"$ne": True}},
        {"symbol": 1, "company_name": 1}
    )
    if limit:
        cursor = cursor.limit(limit)

    for doc in cursor:
        symbol = doc.get("symbol")
        if not symbol:
            continue

        symbol = symbol.upper().strip()
        print(f"\n--- {symbol} ---")

        try:
            json_data = fetch_quote(symbol, session=session, retries=3)
            nse_sections = extract_sections(json_data)

            ipo_past_master.update_one(
                {"symbol": symbol},
                {"$set": {
                    "symbol": symbol,  # normalize stored symbol too
                    "nse_quote": nse_sections,
                    "nse_quote_fetched": True,
                    "nse_quote_error": None,
                    "nse_quote_updated_at": datetime.utcnow(),
                }}
            )

            print(f"✅ Updated NSE quote for {symbol} | ISIN={nse_sections.get('isin')}")
            time.sleep(sleep_seconds)

        except Exception as e:
            # ⚠️ do NOT erase old nse_quote on failure
            ipo_past_master.update_one(
                {"symbol": symbol},
                {"$set": {
                    "nse_quote_fetched": False,
                    "nse_quote_error": str(e),
                    "nse_quote_updated_at": datetime.utcnow(),
                }}
            )
            print(f"⚠️ Failed for {symbol}: {e}")
            time.sleep(sleep_seconds)


if __name__ == "__main__":
    main(limit=None, sleep_seconds=1)
