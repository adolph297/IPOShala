from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

try:
    from iposhala_test.scripts.mongo import ipo_gmp, ipo_live_upcoming, ipo_past_master
    from iposhala_test.scripts.pipeline_gmp import fetch_and_store_gmp
except ImportError:
    from ...scripts.mongo import ipo_gmp, ipo_live_upcoming, ipo_past_master
    from ...scripts.pipeline_gmp import fetch_and_store_gmp

router = APIRouter(prefix="/api/gmp", tags=["GMP Data"])

@router.get("/fetch")
def trigger_fetch_and_store_gmp():
    try:
        data = fetch_and_store_gmp()
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        # If scraping fails, return cached data
        cached_data = list(ipo_gmp.find({}, {"_id": 0}))
        return {"success": False, "message": "Scraping failed, returning cached data", "data": cached_data}

@router.get("/")
def get_gmp_data():
    try:
        # Fetch data sorted by last updated descending
        data = list(ipo_gmp.find({}, {"_id": 0}).sort("lastUpdated", -1))
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
