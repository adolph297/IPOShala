from fastapi import APIRouter
from typing import List
try:
    from iposhala_test.scripts.mongo import ipo_master, ipo_live_upcoming, ipo_past_master
except ImportError:
    from ...scripts.mongo import ipo_master, ipo_live_upcoming, ipo_past_master

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.get("/")
def global_search(q: str = ""):
    if not q or len(q) < 2:
        return []

    # Case-insensitive regex
    regex_query = {"$regex": q, "$options": "i"}
    query = {
        "$or": [
            {"company_name": regex_query},
            {"symbol": regex_query}
        ]
    }

    results = []

    # Search Live/Upcoming
    live_docs = ipo_live_upcoming.find(query, {"_id": 0, "ipo_id": 1, "company_name": 1, "symbol": 1, "status": 1, "security_type": 1}).limit(5)
    for d in live_docs:
        results.append({
            "id": d.get("ipo_id") or d.get("symbol"),
            "name": d.get("company_name"),
            "symbol": d.get("symbol"),
            "type": d.get("security_type", "Equity"),
            "status": d.get("status")
        })

    # Search Past 
    past_docs = ipo_past_master.find(query, {"_id": 0, "ipo_id": 1, "company_name": 1, "symbol": 1, "status": 1, "security_type": 1}).limit(5)
    for d in past_docs:
        results.append({
            "id": d.get("ipo_id") or d.get("symbol"),
            "name": d.get("company_name"),
            "symbol": d.get("symbol"),
            "type": d.get("security_type", "Equity"),
            "status": "Closed"
        })

    # Limit total results to top 10 for autocomplete performance
    return results[:10]
