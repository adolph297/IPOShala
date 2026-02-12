import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nseindia.com/",
}


# ------------------------------------------------------------
# Selenium driver
# ------------------------------------------------------------
def get_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


# ------------------------------------------------------------
# ✅ Persistent NSE cookie session (FAST)
# ------------------------------------------------------------
class NSECookiesSession:
    def __init__(self, headless=True, warmup_symbol="RELIANCE"):
        self.headless = headless
        self.warmup_symbol = warmup_symbol
        self.session = None
        self.updated_at = None

    def refresh(self):
        driver = get_driver(headless=self.headless)
        try:
            url = f"https://www.nseindia.com/get-quotes/equity?symbol={self.warmup_symbol}"
            driver.get(url)
            time.sleep(4)

            cookies = driver.get_cookies()
            cookie_dict = {c["name"]: c["value"] for c in cookies}

            s = requests.Session()
            for k, v in cookie_dict.items():
                s.cookies.set(k, v)

            # warmup
            s.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)

            self.session = s
            self.updated_at = time.time()

        finally:
            driver.quit()

    def get(self) -> requests.Session:
        # refresh if missing or old (30 min)
        if self.session is None or (time.time() - (self.updated_at or 0)) > 1800:
            self.refresh()
        return self.session


cookie_pool = NSECookiesSession(headless=True)


def _safe_get_json(session: requests.Session, url: str):
    res = session.get(url, headers=NSE_HEADERS, timeout=25)
    ct = (res.headers.get("content-type") or "").lower()

    if res.status_code == 404:
        return {"__available__": False, "data": None, "url": url, "code": 404}

    if res.status_code != 200:
        raise Exception(f"NSE Error {res.status_code} | url={url} | body={res.text[:150]}")

    if "application/json" not in ct:
        raise Exception(f"NSE BLOCKED/NOT JSON | ct={ct} | url={url} | body={res.text[:200]}")

    return {"__available__": True, "data": res.json(), "url": url, "code": 200}


def _fetch_with_index_fallback(symbol: str, url_builder):
    s = cookie_pool.get()

    indexes = ["equities", "sme", "debt"]
    last_err = None

    for idx in indexes:
        try:
            url = url_builder(idx)
            res = _safe_get_json(s, url)
            if res.get("__available__"):
                return res
            last_err = Exception(f"Not available in {idx}")
        except Exception as e:
            last_err = e

    # Return 404 result instead of raising
    return {"__available__": False, "data": None, "url": url_builder(indexes[-1]), "code": 404}


# ------------------------------------------------------------
# Existing endpoints
# ------------------------------------------------------------
def selenium_fetch_financial_results(symbol: str):
    return _fetch_with_index_fallback(
        symbol,
        lambda idx: f"https://www.nseindia.com/api/corporates-financial-results?index={idx}&symbol={symbol}"
    )


def selenium_fetch_shareholding_pattern(symbol: str):
    return _fetch_with_index_fallback(
        symbol,
        lambda idx: f"https://www.nseindia.com/api/corporates-share-holding-pattern?index={idx}&symbol={symbol}"
    )


# ------------------------------------------------------------
# Additional sections
# ------------------------------------------------------------
def fetch_announcements(symbol: str):
    return _fetch_with_index_fallback(
        symbol,
        lambda idx: f"https://www.nseindia.com/api/corporate-announcements?index={idx}&symbol={symbol}"
    )


def fetch_annual_reports(symbol: str):
    return _fetch_with_index_fallback(
        symbol,
        lambda idx: f"https://www.nseindia.com/api/annual-reports?index={idx}&symbol={symbol}"
    )


def fetch_brsr_reports(symbol: str):
    return _fetch_with_index_fallback(
        symbol,
        lambda idx: f"https://www.nseindia.com/api/brsr-reports?index={idx}&symbol={symbol}"
    )


def fetch_board_meetings(symbol: str):
    return _fetch_with_index_fallback(
        symbol,
        lambda idx: f"https://www.nseindia.com/api/corporates-board-meetings?index={idx}&symbol={symbol}"
    )


def fetch_corporate_actions(symbol: str):
    return _fetch_with_index_fallback(
        symbol,
        lambda idx: f"https://www.nseindia.com/api/corporates-corporate-actions?index={idx}&symbol={symbol}"
    )


def fetch_event_calendar(symbol: str):
    s = cookie_pool.get()
    url = f"https://www.nseindia.com/api/event-calendar?symbol={symbol}"
    return _safe_get_json(s, url)
