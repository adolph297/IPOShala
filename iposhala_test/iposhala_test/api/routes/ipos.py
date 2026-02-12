from fastapi import APIRouter, HTTPException
from iposhala_test.scripts.mongo import ipo_past_master, MONGO_URI, DB_NAME

router = APIRouter(prefix="/api/ipos", tags=["ipos"])


@router.get("/debug/doc/{symbol}")
def debug_doc(symbol: str):
    symbol = (symbol or "").upper().strip()
    doc = ipo_past_master.find_one({"symbol": symbol})
    if doc:
        doc.pop("_id", None)
    return doc

@router.get("/debug/config")
def debug_config():
    e2erail_count = ipo_past_master.count_documents({"symbol": "E2ERAIL"})
    total_count = ipo_past_master.count_documents({})
    return {
        "mongo_uri": MONGO_URI,
        "db_name": DB_NAME,
        "total_count": total_count,
        "e2erail_count": e2erail_count,
        "client_address": ipo_past_master.database.client.address,
    }


def normalize_symbol(symbol: str) -> str:
    return (symbol or "").upper().strip()


@router.get("/closed")
def get_closed_ipos():
    # existing behavior: list all
    return list(ipo_past_master.find({}, {"_id": 0}))


@router.get("/{symbol}")
def get_ipo_by_symbol(symbol: str):
    symbol = normalize_symbol(symbol)
    ipo = ipo_past_master.find_one({"symbol": symbol}, {"_id": 0})
    if not ipo:
        raise HTTPException(status_code=404, detail="IPO symbol not found")
    
    # ✅ Flatten issue_information for easier frontend access
    info = ipo.get("issue_information", {})
    if info:
        for k, v in info.items():
            if k not in ipo:
                ipo[k] = v

    # ✅ Fallback for missing fields from nse_quote or use official data
    quote = ipo.get("nse_quote", {})
    sec_info = quote.get("security_info", {})
    trade_info = quote.get("trade_info", {})
    
    # Priority: 1. Official Fetched Details, 2. Quote metadata fallback
    if ipo.get("official_issue_size"):
        ipo["issue_size"] = ipo["official_issue_size"]
    elif not ipo.get("issue_size"):
        ipo["issue_size"] = sec_info.get("issuedSize")

    if ipo.get("official_lot_size"):
        ipo["lot_size"] = ipo["official_lot_size"]
    elif not ipo.get("lot_size"):
        ipo["lot_size"] = trade_info.get("marketLot")
                
    return ipo
