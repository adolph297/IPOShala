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
    
    # ✅ Synthesize 'documents' and 'issue_information' for legacy/inconsistent data
    if not ipo.get("documents"):
        ipo_docs = ipo.get("ipo_docs", {})
        if ipo_docs:
            mapping = {
                "ratios": "ratios",
                "rhp": "rhp",
                "bidding_centers": "bidding_centers",
                "forms": "forms",
                "security_pre": "pre-anchor",
                "security_post": "post-anchor",
                "anchor-allocation": "anchor-allocation"
            }
            ipo["documents"] = {}
            for target, source in mapping.items():
                val = ipo_docs.get(source)
                if isinstance(val, dict) and val.get("available"):
                    ipo["documents"][target] = val.get("source_url")

    if not ipo.get("issue_information"):
        add_docs = ipo.get("additional_docs", {})
        if add_docs:
            ipo["issue_information"] = {
                "asba_circular_pdf": add_docs.get("asba_circular"),
                "upi_asba_video": add_docs.get("upi_asba_video"),
                "bhim_upi_registration_video": add_docs.get("bhim_upi_video"),
                "anchor_allocation_zip": ipo.get("documents", {}).get("anchor-allocation")
            }

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
