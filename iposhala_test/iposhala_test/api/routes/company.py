from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Query
from iposhala_test.scripts.mongo import ipo_past_master

router = APIRouter(prefix="/api/company", tags=["company"])


# ---------------------------
# Helpers
# ---------------------------
def normalize_symbol(symbol: str) -> str:
    return (symbol or "").upper().strip()


def fetch(symbol: str, projection: dict):
    symbol = normalize_symbol(symbol)
    doc = ipo_past_master.find_one({"symbol": symbol}, projection)
    if not doc:
        raise HTTPException(status_code=404, detail="Company symbol not found")
    doc.pop("_id", None)
    return doc


def as_list(v) -> List[Any]:
    return v if isinstance(v, list) else []


def paginate(items: List[Any], limit: int, offset: int) -> List[Any]:
    return items[offset: offset + limit]


def sort_by_latest(items: List[Dict], keys: List[str]) -> List[Dict]:
    def k(x):
        for kk in keys:
            val = x.get(kk)
            if val:
                return val
        return ""
    return sorted(items, key=k, reverse=True)


def unwrap_section(section) -> List[Dict]:
    """
    Supports multiple formats:
    1) List: [ {...}, {...} ]
    2) Selenim/New dict: { available: bool, payload: [...], source_url: str } or { data: [...] }
    """
    if not section:
        return []
    if isinstance(section, dict):
        if "payload" in section:
            return section.get("payload") or []
        if "data" in section:
            return section.get("data") or []
        # Support selenium style __available__ or available flags
        if "__available__" in section:
            return section.get("data") or []
    return section if isinstance(section, list) else []


# ---------------------------
# Full company doc
# ---------------------------
@router.get("/{symbol}")
def company_full(symbol: str):
    return fetch(symbol, {"_id": 0})


# ---------------------------
# Quote
# ---------------------------
def normalize_quote(nse_quote: dict):
    if not nse_quote:
        return {}

    price = nse_quote.get("price_info") or {}
    sec = nse_quote.get("security_info") or {}
    trade = nse_quote.get("trade_info") or {}
    meta = nse_quote.get("metadata") or {}
    info = nse_quote.get("info") or {}
    ob = nse_quote.get("order_book") or {}

    return {
        "symbol": meta.get("symbol") or info.get("symbol"),
        "companyName": info.get("companyName"),
        "isin": nse_quote.get("isin") or meta.get("isin") or info.get("isin"),
        "series": meta.get("series"),
        "status": meta.get("status"),
        "listingDate": meta.get("listingDate") or info.get("listingDate"),
        **price,
        "weekHigh": (price.get("weekHighLow") or {}).get("max"),
        "weekLow": (price.get("weekHighLow") or {}).get("min"),
        "securityInfo": sec,
        "tradeInfo": trade,
        "orderBook": ob,
        "metadata": meta,
        "info": info,
    }


@router.get("/{symbol}/quote")
def company_quote(symbol: str):
    doc = fetch(symbol, {"nse_quote": 1})
    nq = doc.get("nse_quote", {}) or {}
    return normalize_quote(nq)


# ---------------------------
# Announcements
# ---------------------------
@router.get("/{symbol}/announcements")
def company_announcements(
    symbol: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    doc = fetch(symbol, {"nse_company.announcements": 1})
    section = (doc.get("nse_company") or {}).get("announcements")
    items = unwrap_section(section)
    items = sort_by_latest(items, ["sort_date", "an_dt", "dt"])
    return paginate(items, limit, offset)


# ---------------------------
# Corporate Actions
# ---------------------------
@router.get("/{symbol}/corporate-actions")
def company_corporate_actions(
    symbol: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    doc = fetch(symbol, {"nse_company.corporate_actions": 1})
    items = as_list((doc.get("nse_company") or {}).get("corporate_actions", []))
    items = sort_by_latest(items, ["exDate", "recordDate", "date"])
    return paginate(items, limit, offset)


# ---------------------------
# Annual Reports
# ---------------------------
@router.get("/{symbol}/annual-reports")
def company_annual_reports(
    symbol: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    doc = fetch(symbol, {"nse_company.annual_reports": 1})
    section = (doc.get("nse_company") or {}).get("annual_reports")
    items = unwrap_section(section)
    items = sort_by_latest(items, ["sort_date", "an_dt", "dt"])
    return paginate(items, limit, offset)


# ---------------------------
# BRSR Reports
# ---------------------------
@router.get("/{symbol}/brsr-reports")
def company_brsr_reports(
    symbol: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    doc = fetch(symbol, {"nse_company.brsr_reports": 1})
    sym = normalize_symbol(symbol)

    section = (doc.get("nse_company") or {}).get("brsr_reports")
    items = unwrap_section(section)

    items = [x for x in items if normalize_symbol(x.get("symbol", "")) == sym]
    items = sort_by_latest(items, ["sort_date", "an_dt", "dt"])
    return paginate(items, limit, offset)


# ---------------------------
# Board Meetings
# ---------------------------
@router.get("/{symbol}/board-meetings")
def company_board_meetings(
    symbol: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    doc = fetch(symbol, {"nse_company.board_meetings": 1})
    items = (doc.get("nse_company") or {}).get("board_meetings", [])

    if isinstance(items, dict) and "data" in items:
        items = items.get("data") or []

    items = as_list(items)
    items = sort_by_latest(items, ["meetingDate", "bm_date", "date", "sort_date"])
    return paginate(items, limit, offset)


# ---------------------------
# Event Calendar
# ---------------------------
@router.get("/{symbol}/event-calendar")
def company_event_calendar(
    symbol: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    doc = fetch(symbol, {"nse_company.event_calendar": 1})
    section = (doc.get("nse_company") or {}).get("event_calendar")
    items = unwrap_section(section)
    items = sort_by_latest(items, ["date", "sort_date"])
    return paginate(items, limit, offset)


# ---------------------------
# Shareholding Pattern
# ---------------------------
@router.get("/{symbol}/shareholding-pattern")
def company_shareholding_pattern(symbol: str):
    doc = fetch(symbol, {
        "nse_company.shareholding_pattern": 1,
        "nse_company.shareholding_patterns": 1
    })
    nse = doc.get("nse_company") or {}
    
    # Priority 1: New historical plural
    plural = nse.get("shareholding_patterns")
    if plural and isinstance(plural, list):
        return plural
        
    # Priority 2: Singular
    return nse.get("shareholding_pattern", {}) or {}


# ---------------------------
# Financial Results
# ---------------------------
@router.get("/{symbol}/financial-results")
def company_financial_results(symbol: str):
    doc = fetch(symbol, {"nse_company.financial_results": 1})
    return (doc.get("nse_company") or {}).get("financial_results", {}) or {}


# ---------------------------
# ✅ Historical performance table (for "Historical Data" tab)
# ---------------------------
@router.get("/{symbol}/historical")
def company_historical(symbol: str):
    symbol = normalize_symbol(symbol)

    doc = ipo_past_master.find_one(
        {"symbol": symbol},
        {"_id": 0, "symbol": 1, "performance_table": 1}
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Company not found")

    return {
        "symbol": symbol,
        "rows": doc.get("performance_table") or []
    }


# ---------------------------
# Tabs summary (frontend friendly)
# ---------------------------
@router.get("/{symbol}/tabs")
def company_tabs_summary(symbol: str):
    doc = fetch(symbol, {
        "symbol": 1,
        "company_name": 1,
        "security_type": 1,
        "nse_company_updated_at": 1,
        "nse_quote_updated_at": 1,

        "nse_company.announcements": 1,
        "nse_company.corporate_actions": 1,
        "nse_company.annual_reports": 1,
        "nse_company.brsr_reports": 1,
        "nse_company.event_calendar": 1,
        "nse_company.board_meetings": 1,
        "nse_company.shareholding_pattern": 1,
        "nse_company.shareholding_patterns": 1,
        "nse_company.audited_financials": 1,
    })

    nse_company = doc.get("nse_company") or {}
    audited_reports = nse_company.get("audited_financials") or []

    announcements = unwrap_section(nse_company.get("announcements"))
    annual_reports = unwrap_section(nse_company.get("annual_reports"))
    brsr_reports = unwrap_section(nse_company.get("brsr_reports"))
    corporate_actions = unwrap_section(nse_company.get("corporate_actions"))
    event_calendar = unwrap_section(nse_company.get("event_calendar"))
    board_meetings = unwrap_section(nse_company.get("board_meetings"))

    # Handle shareholding pattern logic for tabs summary
    shareholding = nse_company.get("shareholding_patterns") or nse_company.get("shareholding_pattern") or {}
    financials = nse_company.get("financial_results") or {}

    ANN_PREVIEW = 5
    ACTIONS_PREVIEW = 5
    REPORTS_PREVIEW = 3

    return {
        "symbol": doc.get("symbol"),
        "company_name": doc.get("company_name"),
        "security_type": doc.get("security_type"),
        "updated_at": {
            "nse_company_updated_at": doc.get("nse_company_updated_at"),
            "nse_quote_updated_at": doc.get("nse_quote_updated_at"),
        },
        "tabs": {
            "announcements": {"count": len(announcements), "preview": announcements[:ANN_PREVIEW]},
            "corporate_actions": {"count": len(corporate_actions), "preview": corporate_actions[:ACTIONS_PREVIEW]},
            "annual_reports": {"count": len(annual_reports), "preview": annual_reports[:REPORTS_PREVIEW]},
            "brsr_reports": {"count": len(brsr_reports), "preview": brsr_reports[:REPORTS_PREVIEW]},
            "event_calendar": {"count": len(event_calendar), "preview": event_calendar[:ACTIONS_PREVIEW]},
            "board_meetings": {"count": len(board_meetings), "preview": board_meetings[:ACTIONS_PREVIEW]},
            "shareholding_pattern": {
                "exists": shareholding not in (None, {}, []),
                "data": shareholding,
            },
            "financial_results": {
                "exists": financials not in (None, {}, []),
                "data": financials,
            },
            "audited_financials": {
                "exists": len(audited_reports) > 0,
                "data": audited_reports,
            },
        }
    }
