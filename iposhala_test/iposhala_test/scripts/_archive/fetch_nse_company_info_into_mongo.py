from datetime import datetime, timezone
import time
import requests

from iposhala_test.scripts.mongo import ipo_past_master

from iposhala_test.scrapers.nse_company_dynamic import (
    selenium_fetch_shareholding_pattern,
    selenium_fetch_financial_results,
    fetch_announcements,
    fetch_annual_reports,
    fetch_brsr_reports,
    fetch_board_meetings,
    fetch_event_calendar,
    fetch_corporate_actions,
)

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}


def utcnow():
    return datetime.now(timezone.utc)


def ensure_dict(x):
    return x if isinstance(x, dict) else {}


def get_session():
    s = requests.Session()
    s.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)  # warmup cookies
    return s


def safe_get_json(session: requests.Session, url: str, retries: int = 3):
    """
    NSE can return HTML (blocked) even when status=200.
    This function retries and refreshes warmup cookies.
    """
    last_err = None

    for i in range(retries):
        try:
            r = session.get(url, headers=NSE_HEADERS, timeout=20)

            # retry on 401/403
            if r.status_code in (401, 403):
                warmup(session)
                time.sleep(1.5 + i)
                continue

            if r.status_code == 404:
                return {"__not_found__": True}

            r.raise_for_status()

            ct = (r.headers.get("content-type") or "").lower()

            # ✅ NSE blocked HTML detection
            if "application/json" not in ct:
                raise Exception(
                    f"Blocked/non-json response ct={ct}, sample={r.text[:200]}"
                )

            return r.json()

        except Exception as e:
            last_err = e
            time.sleep(1.5 + i)  # backoff

            # refresh cookies on retry
            try:
                warmup(session)
            except Exception:
                pass

    raise last_err



def _requests_with_index_fallback(session: requests.Session, url_builder):
    indexes = ["equities", "sme", "debt"]
    for idx in indexes:
        try:
            res = safe_get_json(session, url_builder(idx))
            if res and not res.get("__not_found__"):
                return res
        except Exception:
            pass
    return None


# ---------------------------
# NSE APIs (requests-first)
# ---------------------------

def fetch_shareholding_pattern(session: requests.Session, symbol: str, isin: str):
    try:
        return _requests_with_index_fallback(
            session,
            lambda idx: f"https://www.nseindia.com/api/corporates-share-holding-pattern?index={idx}&symbol={symbol}"
        )
    except Exception:
        return _requests_with_index_fallback(
            session,
            lambda idx: f"https://www.nseindia.com/api/corporates-share-holding-pattern?index={idx}&isin={isin}"
        )


def fetch_financial_results(session: requests.Session, symbol: str, isin: str):
    try:
        return _requests_with_index_fallback(
            session,
            lambda idx: f"https://www.nseindia.com/api/corporates-financial-results?index={idx}&symbol={symbol}"
        )
    except Exception:
        return _requests_with_index_fallback(
            session,
            lambda idx: f"https://www.nseindia.com/api/corporates-financial-results?index={idx}&isin={isin}"
        )


def fetch_board_meetings_requests(session: requests.Session, symbol: str, isin: str):
    try:
        return _requests_with_index_fallback(
            session,
            lambda idx: f"https://www.nseindia.com/api/corporates-board-meetings?index={idx}&symbol={symbol}"
        )
    except Exception:
        return _requests_with_index_fallback(
            session,
            lambda idx: f"https://www.nseindia.com/api/corporates-board-meetings?index={idx}&isin={isin}"
        )


def fetch_event_calendar_requests(session: requests.Session, symbol: str, isin: str):
    try:
        url = f"https://www.nseindia.com/api/event-calendar?symbol={symbol}"
        return safe_get_json(session, url)
    except Exception:
        url = f"https://www.nseindia.com/api/event-calendar?isin={isin}"
        return safe_get_json(session, url)


def main(limit=None):
    print(">>> FETCHING NSE COMPANY SECTIONS INTO MONGODB <<<")

    session = get_session()

    cursor = ipo_past_master.find(
        {"nse_quote_fetched": True, "nse_quote.isin": {"$ne": None}},
        {"symbol": 1, "company_name": 1, "nse_quote.isin": 1}
    )

    if limit is not None:
        cursor = cursor.limit(limit)

    for idx, doc in enumerate(cursor, start=1):
        if idx % 50 == 0:
            session = get_session()

        symbol = (doc.get("symbol") or "").upper().strip()
        isin = (doc.get("nse_quote") or {}).get("isin")

        if not symbol or not isin:
            continue

        print(f"\n--- {symbol} | ISIN={isin} ---")
        dynamic_error = {}

        try:
            shareholding_pattern = None
            financial_results = None
            board_meetings = None
            event_calendar = None
            announcements = None
            annual_reports = None
            brsr_reports = None
            corporate_actions = None

            # ✅ Shareholding pattern
            try:
                sp = fetch_shareholding_pattern(session, symbol, isin)
                sp = ensure_dict(sp)
                if sp:
                    shareholding_pattern = sp
                print("  shareholding_pattern: ok (requests)")
            except Exception as e:
                print(f"⚠️ shareholding_pattern requests failed: {e}")
                try:
                    sp = selenium_fetch_shareholding_pattern(symbol)
                    sp = ensure_dict(sp)
                    if sp:
                        shareholding_pattern = sp
                    print("  shareholding_pattern: ok (selenium-cookie)")
                except Exception as se:
                    dynamic_error["shareholding_pattern"] = str(se)
                    print(f"❌ shareholding_pattern selenium-cookie failed: {se}")

            # ✅ Financial results
            try:
                fr = fetch_financial_results(session, symbol, isin)
                fr = ensure_dict(fr)
                if fr:
                    financial_results = fr
                print("  financial_results: ok (requests)")
            except Exception as e:
                print(f"⚠️ financial_results requests failed: {e}")
                try:
                    fr = selenium_fetch_financial_results(symbol)
                    fr = ensure_dict(fr)
                    if fr:
                        financial_results = fr
                    print("  financial_results: ok (selenium-cookie)")
                except Exception as se:
                    dynamic_error["financial_results"] = str(se)
                    print(f"❌ financial_results selenium-cookie failed: {se}")

            # ✅ Board meetings
            try:
                bm = fetch_board_meetings_requests(session, symbol, isin)
                board_meetings = bm
                print("  board_meetings: ok (requests)")
            except Exception as e:
                print(f"⚠️ board_meetings requests failed: {e}")
                try:
                    bm = fetch_board_meetings(symbol)
                    board_meetings = bm
                    print("  board_meetings: ok (selenium-cookie)")
                except Exception as se:
                    dynamic_error["board_meetings"] = str(se)
                    print(f"❌ board_meetings selenium-cookie failed: {se}")

            # ✅ Event calendar
            try:
                ec = fetch_event_calendar_requests(session, symbol, isin)
                event_calendar = ec
                print("  event_calendar: ok (requests)")
            except Exception as e:
                print(f"⚠️ event_calendar requests failed: {e}")
                try:
                    ec = fetch_event_calendar(symbol)
                    event_calendar = ec
                    print("  event_calendar: ok (selenium-cookie)")
                except Exception as se:
                    dynamic_error["event_calendar"] = str(se)
                    print(f"❌ event_calendar selenium-cookie failed: {se}")

            # ✅ Corporate actions
            try:
                ca = fetch_corporate_actions(symbol)
                items = ca.get("data") if ca.get("__available__") else []
                if isinstance(items, dict) and "data" in items:
                    items = items.get("data")
                if isinstance(items, list):
                    items = [x for x in items if (x.get("symbol") or "").upper() == symbol]
                else:
                    items = []
                corporate_actions = {
                    "available": True if items else False,
                    "payload": items,
                    "source_url": ca.get("url")
                }
                print("  corporate_actions: ok")
            except Exception as e:
                print(f"⚠️ corporate_actions failed: {e}")

            # ✅ Announcements
            try:
                ann = fetch_announcements(symbol)
                items = ann.get("data") if ann.get("__available__") else []
                if isinstance(items, dict) and "data" in items:
                    items = items.get("data")

                if isinstance(items, list):
                    items = [x for x in items if (x.get("symbol") or "").upper() == symbol]
                else:
                    items = []
                announcements = {
                    "available": True if items else False,
                    "payload": items,
                    "source_url": ann.get("url")
                }
                print("  announcements: ok")
            except Exception as e:
                print(f"⚠️ announcements failed: {e}")

            # ✅ Annual reports
            try:
                ar = fetch_annual_reports(symbol)
                items = ar.get("data") if ar.get("__available__") else []
                if isinstance(items, list):
                    items = [x for x in items if (x.get("symbol") or "").upper() == symbol]
                annual_reports = {
                    "available": True if items else False,
                    "payload": items,
                    "source_url": ar.get("url")
                }
                print("  annual_reports: ok")
            except Exception as e:
                print(f"⚠️ annual_reports failed: {e}")

            # ✅ BRSR reports
            try:
                br = fetch_brsr_reports(symbol)
                items = br.get("data") if br.get("__available__") else []
                if isinstance(items, list):
                    items = [x for x in items if (x.get("symbol") or "").upper() == symbol]
                brsr_reports = {
                    "available": True if items else False,
                    "payload": items,
                    "source_url": br.get("url")
                }
                print("  brsr_reports: ok")
            except Exception as e:
                print(f"⚠️ brsr_reports failed: {e}")

            update_payload = {
                "nse_company_dynamic_fetched": True,
                "nse_company_dynamic_updated_at": utcnow(),
                "nse_company_dynamic_error": dynamic_error or None,
            }

            if shareholding_pattern is not None:
                update_payload["nse_company.shareholding_pattern"] = shareholding_pattern
            if financial_results is not None:
                update_payload["nse_company.financial_results"] = financial_results
            if board_meetings is not None:
                update_payload["nse_company.board_meetings"] = board_meetings
            if event_calendar is not None:
                update_payload["nse_company.event_calendar"] = event_calendar
            if announcements is not None:
                update_payload["nse_company.announcements"] = announcements
            if annual_reports is not None:
                update_payload["nse_company.annual_reports"] = annual_reports
            if brsr_reports is not None:
                update_payload["nse_company.brsr_reports"] = brsr_reports
            if corporate_actions is not None:
                update_payload["nse_company.corporate_actions"] = corporate_actions

            ipo_past_master.update_one({"symbol": symbol}, {"$set": update_payload})

            print(f"✅ Stored company sections for {symbol}")
            time.sleep(0.5)

        except Exception as e:
            ipo_past_master.update_one(
                {"symbol": symbol},
                {"$set": {
                    "nse_company_dynamic_fetched": False,
                    "nse_company_dynamic_error": {"__fatal__": str(e)},
                    "nse_company_dynamic_updated_at": utcnow(),
                }}
            )
            print(f"❌ Failed for {symbol}: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main(limit=None)
