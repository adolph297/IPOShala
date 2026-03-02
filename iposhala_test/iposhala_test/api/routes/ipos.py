from fastapi import APIRouter, HTTPException
from iposhala_test.scripts.mongo import ipo_past_master, ipo_live_upcoming, MONGO_URI, DB_NAME
from datetime import datetime

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





@router.get("/{identifier}")
def get_ipo(identifier: str):
    print(f"DEBUG API REQ: /{identifier}")
    identifier = identifier.strip()
    
    ipo = ipo_past_master.find_one({"ipo_id": identifier.lower()}, {"_id": 0})
    print(f"DEBUG IPO by ipo_id: {bool(ipo)}")
    if not ipo:
        ipo = ipo_past_master.find_one({"symbol": identifier.upper()}, {"_id": 0})
        print(f"DEBUG IPO by symbol: {bool(ipo)}")

    if not ipo:
        live_ipo = ipo_live_upcoming.find_one({"ipo_id": identifier.lower()}, {"_id": 0})
        if not live_ipo:
            live_ipo = ipo_live_upcoming.find_one({"symbol": identifier.upper()}, {"_id": 0})
            
        if not live_ipo:
            raise HTTPException(status_code=404, detail="IPO symbol not found")
        
        # Parse datetime into strings for JSON streaming
        start = live_ipo.get("issue_start_date")
        end = live_ipo.get("issue_end_date")
        start_str = start.isoformat() if isinstance(start, datetime) else start
        end_str = end.isoformat() if isinstance(end, datetime) else end

        ipo = {
            "ipo_id": live_ipo.get("ipo_id"),
            "symbol": live_ipo.get("symbol"),
            "company_name": live_ipo.get("company_name", live_ipo.get("symbol")),
            "security_type": live_ipo.get("security_type", "Equity"),
            "issue_start_date": start_str,
            "issue_end_date": end_str,
            "issue_price": live_ipo.get("price_range", "-"),
            "price_range": live_ipo.get("price_range", "-"),
            "status": live_ipo.get("status", "LIVE"),
            "issue_information": {
                "issue_price": live_ipo.get("price_range", "-"),
                "issue_size": live_ipo.get("issue_size", "-"),
                "issue_start_date": start_str,
                "issue_end_date": end_str
            },
            "documents": {},
            "nse_company": {}
        }
    
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
        
    # ✅ Calculate Risk / Confidence Score
    confidence = 50
    try:
        gmp_val = float(ipo.get("gmp", 0) or 0)
        
        # parse issue price to get upper band
        price_str = str(ipo.get("issue_price") or ipo.get("price_range") or "0")
        import re
        prices = [int(p) for p in re.findall(r'\d+', price_str.replace(',', ''))]
        upper_price = max(prices) if prices else 0
        
        if upper_price > 0:
            gmp_pct = (gmp_val / upper_price) * 100
            if gmp_pct > 50:
                confidence += 30
            elif gmp_pct > 20:
                confidence += 20
            elif gmp_pct > 0:
                confidence += 10
            elif gmp_pct < 0:
                confidence -= 20
                
        # Subscriptions
        sub = ipo.get("subscription", {})
        qib = float(sub.get("qib") or 0)
        hni = float(sub.get("hni") or sub.get("nii") or 0)
        retail = float(sub.get("retail") or 0)
        
        total_sub = qib + hni + retail
        if qib > 50:
            confidence += 20
        elif qib > 10:
            confidence += 10
            
        if total_sub > 100:
            confidence += 10
            
        # Issue Size
        size_str = str(ipo.get("issue_size", "0"))
        sizes = [float(p) for p in re.findall(r'\d+\.?\d*', size_str.replace(',',''))]
        size_val = max(sizes) if sizes else 0
        if size_val > 1000: # > 1000 Cr usually more stable
            confidence += 10
        elif size_val < 100 and size_val > 0: # SME or small
            confidence -= 10
            
    except Exception as e:
        print(f"Risk calc error: {e}")
        pass
        
    ipo["confidence_score"] = min(100, max(0, confidence))
    
    if ipo["confidence_score"] >= 75:
        ipo["risk_level"] = "Low Risk / High Reward"
    elif ipo["confidence_score"] >= 45:
        ipo["risk_level"] = "Moderate"
    else:
        ipo["risk_level"] = "High Risk / Speculative"
                
    return ipo
