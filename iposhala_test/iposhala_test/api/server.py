from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from .routes.ipos import router as ipos_router
from .routes.company import router as company_router
import requests
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

app.include_router(ipos_router)
app.include_router(company_router)
app.include_router(docs_router)

@app.get("/api/ipos/closed")
def get_closed_ipos():
    docs = list(
        ipo_past_master.find(
            {"exchange": "NSE"},
            {
                "_id": 0,
                "company_name": 1,
                "symbol": 1,
                "security_type": 1,
                "issue_information.issue_end_date": 1,
                "issue_information.issue_price": 1,
            }
        )
    )

    def parse_date(s):
        if not s or s == "-":
            return None
        try:
            return datetime.strptime(s.strip(), "%d-%b-%Y")
        except Exception:
            return None

    today = datetime.today()

    closed = []
    for d in docs:
        end_date = parse_date((d.get("issue_information") or {}).get("issue_end_date"))
        if end_date and end_date < today:
            closed.append(d)

    # sort latest closed first
    closed.sort(
        key=lambda x: parse_date((x.get("issue_information") or {}).get("issue_end_date")) or datetime.min,
        reverse=True
    )

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