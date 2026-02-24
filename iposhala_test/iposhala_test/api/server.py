from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from .routes.ipos import router as ipos_router
from .routes.company import router as company_router
import requests
from datetime import datetime
from iposhala_test.api.routes.docs import router as docs_router


# Import Mongo collection
from iposhala_test.scripts.mongo import ipo_past_master

app = FastAPI(title="IPOShala Backend API")

nse_headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nseindia.com/",
}

# Allow frontend (Vite / React) to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/ipos/closed")
def get_closed_ipos():
    docs = list(
        ipo_past_master.find(
            {},
            {
                "_id": 0,
                "company_name": 1,
                "symbol": 1,
                "security_type": 1,
                "issue_information.issue_end_date": 1,
                "issue_information.issue_price": 1,
                "issue_end_date": 1,
                "nse_quote.metadata.listingDate": 1,
                "price_range": 1
            }
        )
    )

    def parse_date(s):
        if not s or s == "-":
            return None
        s = s.strip()
        for fmt in ("%d-%b-%Y", "%d-%b-%y", "%Y-%m-%d", "%d-%m-%Y", "%B %d, %Y"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        return None

    today = datetime.today()

    closed = []
    for d in docs:
        info = d.get("issue_information") or {}
        end_date_str = info.get("issue_end_date") or d.get("issue_end_date")
        
        # Look for listingDate from NSE quote metadata if still missing
        if not end_date_str:
            metadata = d.get("nse_quote", {}).get("metadata", {})
            end_date_str = metadata.get("listingDate")

        end_date = parse_date(end_date_str)
        if end_date and end_date < today:
            price = info.get("issue_price") or d.get("price_range") or "-"
            
            parsed = {
                "company_name": d.get("company_name", d.get("symbol")),
                "symbol": d.get("symbol"),
                "security_type": d.get("security_type", "Equity"),
                "issue_end_date": end_date_str if end_date_str else "-",
                "issue_price": price,
                "status": "Closed",
                "_parsed_date": end_date # For sorting only
            }
            closed.append(parsed)

    # sort latest closed first
    closed.sort(key=lambda x: x.pop("_parsed_date"), reverse=True)

    return closed


app.include_router(ipos_router)
app.include_router(company_router)
app.include_router(docs_router)

@app.get("/api/ipos/closed")
def get_closed_ipos():
    docs = list(
        ipo_past_master.find(
            {},
            {
                "_id": 0,
                "company_name": 1,
                "symbol": 1,
                "security_type": 1,
                "issue_information.issue_end_date": 1,
                "issue_information.issue_price": 1,
                "issue_end_date": 1,
                "nse_quote.metadata.listingDate": 1,
                "price_range": 1
            }
        )
    )

    def parse_date(s):
        if not s or s == "-":
            return None
        s = s.strip()
        for fmt in ("%d-%b-%Y", "%d-%b-%y", "%Y-%m-%d", "%d-%m-%Y", "%B %d, %Y"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        return None

    today = datetime.today()

    closed = []
    for d in docs:
        info = d.get("issue_information") or {}
        end_date_str = info.get("issue_end_date") or d.get("issue_end_date")
        
        # Look for listingDate from NSE quote metadata if still missing
        if not end_date_str:
            metadata = d.get("nse_quote", {}).get("metadata", {})
            end_date_str = metadata.get("listingDate")

        end_date = parse_date(end_date_str)
        if end_date and end_date < today:
            price = info.get("issue_price") or d.get("price_range") or "-"
            
            parsed = {
                "company_name": d.get("company_name", d.get("symbol")),
                "symbol": d.get("symbol"),
                "security_type": d.get("security_type", "Equity"),
                "issue_end_date": end_date_str if end_date_str else "-",
                "issue_price": price,
                "status": "Closed",
                "_parsed_date": end_date # For sorting only
            }
            closed.append(parsed)

    # sort latest closed first
    closed.sort(key=lambda x: x.pop("_parsed_date"), reverse=True)

    return closed


@app.get("/api/ipos/{symbol}")
def get_ipo_by_symbol(symbol: str):
    ipo = ipo_past_master.find_one(
        {"symbol": symbol},
        {"_id": 0}
    )

    if not ipo:
        raise HTTPException(status_code=404, detail="IPO not found")

    return ipo

@app.get("/api/nse/quote/{symbol}")
def get_nse_quote(symbol: str):
    session = requests.Session()

    # warm up to get cookies
    session.get("https://www.nseindia.com", headers=nse_headers, timeout=10)

    api_url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol.upper()}"
    res = session.get(api_url, headers=nse_headers, timeout=10)

    return res.json()