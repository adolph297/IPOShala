import requests
from bs4 import BeautifulSoup
from datetime import datetime, UTC
import time

from iposhala_test.scripts.mongo import ipo_past_master
from iposhala_test.scrapers.nse_company_dynamic import cookie_pool, NSE_HEADERS


NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nseindia.com/",
}


def normalize_symbol(symbol: str) -> str:
    return (symbol or "").upper().strip()


def warmup(session: requests.Session):
    session.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)


def extract_download_links(html: str):
    soup = BeautifulSoup(html, "html.parser")

    result = {}

    # collect all <a> tag links
    for a in soup.find_all("a"):
        label = (a.get_text() or "").strip().lower()
        href = (a.get("href") or "").strip()

        if not href or href.startswith("javascript"):
            continue

        # Map label -> DB field
        if "ratios" in label or "basis of issue" in label:
            result["ratios_basis_issue_price"] = href
        elif "red herring" in label:
            result["red_herring_prospectus"] = href
        elif "bidding centers" in label:
            result["bidding_centers"] = href
        elif "sample application" in label:
            result["sample_application_forms"] = href
        elif "security parameters" in label and "pre" in label:
            result["security_parameters_pre_anchor"] = href
        elif "security parameters" in label and "post" in label:
            result["security_parameters_post_anchor"] = href
        elif "anchor allocation report" in label:
            result["anchor_allocation_report"] = href

    return result


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



def fetch_docs_for_symbol(symbol: str, security_type: str) -> dict:
    """
    Uses NSE IPO endpoint. Handles API returning list OR dict.
    Returns doc URLs.
    """
    sym = normalize_symbol(symbol)
    session = cookie_pool.get()

    series = "SME" if (security_type or "").upper() == "SME" else "EQ"
    url = f"https://www.nseindia.com/market-data/issue-information?symbol={sym}&series={series}&type=Past"

    data = safe_get_json(session, url)

    # ✅ NSE sometimes returns list, sometimes dict
    if isinstance(data, list):
        issues = data
    elif isinstance(data, dict):
        issues = data.get("data") or data.get("result") or []
        if not isinstance(issues, list):
            issues = []
    else:
        issues = []

    # find matching symbol
    issue = None
    for x in issues:
        if isinstance(x, dict) and normalize_symbol(x.get("symbol")) == sym:
            issue = x
            break

    if not issue:
        return {}

    docs = {}

    def put(k, v):
        if v and isinstance(v, str) and v.startswith("http"):
            docs[k] = v

    # ✅ best-effort mapping (keys vary)
    put("red_herring_prospectus", issue.get("rhpDocument") or issue.get("rhp") or issue.get("rhpPdf"))
    put("anchor_allocation_report", issue.get("anchorDocument") or issue.get("anchorAllocationReport"))
    put("ratios_basis_issue_price", issue.get("basisOfIssuePrice") or issue.get("basisOfAllotment"))

    # sometimes there is a documents array
    documents = issue.get("documents") or []
    if isinstance(documents, list):
        for d in documents:
            if not isinstance(d, dict):
                continue

            name = (d.get("name") or d.get("title") or "").lower()
            link = d.get("url") or d.get("link")
            if not link:
                continue

            if "rhp" in name or "red herring" in name:
                put("red_herring_prospectus", link)
            elif "bidding" in name:
                put("bidding_centers", link)
            elif "sample application" in name:
                put("sample_application_forms", link)
            elif "security parameters" in name and "pre" in name:
                put("security_parameters_pre_anchor", link)
            elif "security parameters" in name and "post" in name:
                put("security_parameters_post_anchor", link)
            elif "anchor allocation" in name:
                put("anchor_allocation_report", link)
            elif "ratios" in name or "basis of issue" in name:
                put("ratios_basis_issue_price", link)

    return docs


def to_ipo_docs_schema(docs: dict) -> dict:
    """
    Convert your existing keys into the new Mode-B schema expected by /api/docs.
    """
    mapping = {
        "ratios_basis_issue_price": "ratios",
        "red_herring_prospectus": "rhp",
        "bidding_centers": "bidding-centers",
        "sample_application_forms": "forms",
        "security_parameters_pre_anchor": "pre-anchor",
        "security_parameters_post_anchor": "post-anchor",
        "anchor_allocation_report": "anchor-allocation",
    }

    out = {}
    for old_key, doc_type in mapping.items():
        url = docs.get(old_key)
        if url:
            out[doc_type] = {
                "available": True,
                "source_url": url,
                "updated_at": datetime.now(UTC),
            }
        else:
            out[doc_type] = {
                "available": False,
                "source_url": None,
                "updated_at": datetime.now(UTC),
            }

    return out


def main():
    cursor = ipo_past_master.find(
        {"exchange": "NSE"},
        {"symbol": 1, "security_type": 1}
    )

    for row in cursor:
        sym = normalize_symbol(row.get("symbol"))
        security_type = (row.get("security_type") or "").upper().strip()

        if not sym:
            continue

        if not security_type:
            # default fallback
            security_type = "EQ"

        print(f"\n=== Fetch IPO docs for {sym} | security_type={security_type} ===")

        try:
            # ✅ FIXED: pass security_type
            docs = fetch_docs_for_symbol(sym, security_type)

        except Exception as e:
            print("❌ Error:", str(e))
            ipo_past_master.update_one(
                {"symbol": sym},
                {"$set": {
                    "nse_ipo_docs_fetched": False,
                    "nse_ipo_docs_error": str(e),
                    "nse_ipo_docs_updated_at": datetime.now(UTC),
                }}
            )
            time.sleep(0.4)
            continue

        if not docs:
            print("⚠️ No docs found for this symbol")
            ipo_past_master.update_one(
                {"symbol": sym},
                {"$set": {
                    "nse_ipo_docs_fetched": False,
                    "nse_ipo_docs_error": "No links extracted",
                    "nse_ipo_docs_updated_at": datetime.now(UTC),
                }}
            )
            continue

        # ✅ Build update payload
        now = datetime.now(UTC)

        set_fields = {
            "nse_ipo_docs_fetched": True,
            "nse_ipo_docs_error": None,
            "nse_ipo_docs_updated_at": now,
        }

        # ------------------------------------------------------------
        # ✅ OLD STYLE (optional): store under issue_information.*
        # (you can remove this if you no longer want it)
        # ------------------------------------------------------------
        for k, v in docs.items():
            set_fields[f"issue_information.{k}"] = v

        # ------------------------------------------------------------
        # ✅ NEW STYLE (required for Mode B):
        # store under ipo_docs.<doc_type>.source_url
        # ------------------------------------------------------------
        ipo_docs_payload = to_ipo_docs_schema(docs)
        set_fields["ipo_docs"] = ipo_docs_payload

        ipo_past_master.update_one({"symbol": sym}, {"$set": set_fields})
        print("✅ Updated Mongo with IPO docs keys:", list(docs.keys()))

        time.sleep(0.25)


if __name__ == "__main__":
    main()
