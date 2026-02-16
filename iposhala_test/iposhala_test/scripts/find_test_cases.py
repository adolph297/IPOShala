from iposhala_test.scripts.mongo import ipo_past_master
import json

def find_test_cases():
    # Fields to check
    fields = [
        "shareholding_patterns",
        "event_calendar",
        "annual_reports"
    ]
    
    print("Searching for companies with multiple data types...")
    
    query = {
        "$and": [
            {"nse_company.shareholding_patterns": {"$exists": True, "$not": {"$size": 0}}},
            {
                "$or": [
                    {f"nse_company.event_calendar": {"$type": "array", "$ne": []}},
                    {f"nse_company.event_calendar.available": True},
                    {f"nse_company.event_calendar.payload": {"$exists": True, "$ne": []}}
                ]
            },
            {
                "$or": [
                    {f"nse_company.annual_reports": {"$type": "array", "$ne": []}},
                    {f"nse_company.annual_reports.available": True},
                    {f"nse_company.annual_reports.payload": {"$exists": True, "$ne": []}}
                ]
            }
        ]
    }
    
    projection = {
        "symbol": 1,
        "nse_company.shareholding_patterns": 1,
        "nse_company.event_calendar": 1,
        "nse_company.annual_reports": 1
    }
    
    results = list(ipo_past_master.find(query, projection).limit(10))
    
    if not results:
        print("No companies found with all 3 data types. Loosening criteria...")
        # Check for any 2
        # ... just showing top symbols with ANY data for now
        return

    print(f"Found {len(results)} companies with Shareholding + Event Calendar + Annual Reports:")
    for doc in results:
        symbol = doc.get("symbol")
        sh_count = len(doc.get("nse_company", {}).get("shareholding_patterns", []))
        print(f"- {symbol} (SH: {sh_count} records)")

if __name__ == "__main__":
    find_test_cases()
