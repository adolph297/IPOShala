from iposhala_test.scripts.mongo import ipo_past_master
import json

def find_strict_test_cases():
    query = {
        "$and": [
            {"nse_company.shareholding_patterns": {"$exists": True, "$not": {"$size": 0}}},
            {"nse_company.event_calendar.payload": {"$exists": True, "$not": {"$size": 0}}},
            {"nse_company.annual_reports.payload": {"$exists": True, "$not": {"$size": 0}}}
        ]
    }
    
    projection = {
        "symbol": 1,
        "nse_company.shareholding_patterns": 1,
        "nse_company.event_calendar.payload": 1,
        "nse_company.annual_reports.payload": 1
    }
    
    results = list(ipo_past_master.find(query, projection).limit(5))
    
    if not results:
        print("No companies found with STIRCT non-empty payloads for all 3 types.")
        return

    print(f"Found {len(results)} companies with STRICT data:")
    for doc in results:
        symbol = doc.get("symbol")
        sh_count = len(doc.get("nse_company", {}).get("shareholding_patterns", []))
        ev_count = len(doc.get("nse_company", {}).get("event_calendar", {}).get("payload", []))
        an_count = len(doc.get("nse_company", {}).get("annual_reports", {}).get("payload", []))
        print(f"- {symbol} (SH: {sh_count}, EV: {ev_count}, AN: {an_count})")

if __name__ == "__main__":
    find_strict_test_cases()
