# iposhala_test/api/routes/docs.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import time
from typing import Optional

from iposhala_test.scripts.mongo import ipo_past_master

router = APIRouter(prefix="/api/docs", tags=["docs"])

# ✅ Headers for PDF download from NSE
NSE_PDF_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/pdf,application/octet-stream,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}


def normalize_symbol(symbol: str) -> str:
    return (symbol or "").upper().strip()


def map_doc_type(doc_type: str) -> str:
    doc_type = (doc_type or "").strip().lower()

    aliases = {
        "ratios": "ratios",
        "rhp": "rhp",
        "bidding_centers": "bidding_centers",
        "forms": "forms",
        "security_pre": "security_pre",
        "security_post": "security_post",
        "anchor-allocation": "anchor-allocation",
    }

    if doc_type not in aliases:
        raise HTTPException(status_code=400, detail=f"Invalid doc_type: {doc_type}")

    return aliases[doc_type]


def get_doc_source_url(symbol: str, doc_type: str) -> Optional[str]:
    symbol = normalize_symbol(symbol)

    doc = ipo_past_master.find_one(
        {"symbol": symbol},
        {"documents": 1, "symbol": 1, "_id": 0}
    )

    if not doc:
        return None

    documents = doc.get("documents") or {}
    return documents.get(doc_type)


def get_nse_session() -> requests.Session:
    """
    Creates a session and warms up NSE cookies.
    """
    s = requests.Session()
    s.get("https://www.nseindia.com", headers=NSE_PDF_HEADERS, timeout=15)
    return s


def stream_doc_from_url(url: str, filename: str):
    """
    Stream NSE PDF or ZIP. Retries if blocked.
    """
    last_err = None

    for attempt in range(1, 5):
        try:
            session = get_nse_session()
            
            # Use different headers for different attempts to try bypassing blocks
            current_headers = NSE_PDF_HEADERS.copy()
            if attempt > 1:
                current_headers["Upgrade-Insecure-Requests"] = "1"
            
            r = session.get(url, headers=current_headers, stream=True, timeout=30)

            if r.status_code != 200:
                # If we get 503 or 403, it's likely a temporary block or rate limit
                if r.status_code in [503, 403, 429]:
                    time.sleep(2 * attempt)
                    continue
                raise Exception(f"NSE status={r.status_code}")

            ct = (r.headers.get("Content-Type") or "").lower()

            # NSE sometimes returns HTML block page even with 200
            if "pdf" not in ct and "octet-stream" not in ct and "zip" not in ct:
                sample = ""
                try:
                    sample = r.text[:200]
                except Exception:
                    pass
                raise Exception(f"Blocked/non-document response ct={ct}, sample={sample}")

            # Determine filename extension if not already in filename
            final_filename = filename
            if "zip" in ct and not final_filename.endswith(".zip"):
                final_filename += ".zip"
            elif "pdf" in ct and not final_filename.endswith(".pdf"):
                final_filename += ".pdf"

            return StreamingResponse(
                r.iter_content(chunk_size=1024 * 128),
                media_type=r.headers.get("Content-Type", "application/pdf"),
                headers={
                    "Content-Disposition": f'inline; filename="{final_filename}"',
                    "Cache-Control": "no-store",
                },
            )

        except Exception as e:
            last_err = e
            time.sleep(1 * attempt)

    raise HTTPException(status_code=502, detail=f"Failed to fetch NSE PDF: {last_err}")


@router.get("/{symbol}/{doc_type}")
def stream_ipo_doc(symbol: str, doc_type: str):
    symbol = normalize_symbol(symbol)
    doc_type = map_doc_type(doc_type)

    source_url = get_doc_source_url(symbol, doc_type)

    # ✅ OPTION B: Never 404. Always return something.
    if not source_url:
        return JSONResponse(
            status_code=200,
            content={
                "available": False,
                "symbol": symbol,
                "doc_type": doc_type,
                "message": "Document not available for this IPO (NSE link missing).",
            },
        )

    filename = f"{symbol}_{doc_type}"
    return stream_doc_from_url(source_url, filename)
