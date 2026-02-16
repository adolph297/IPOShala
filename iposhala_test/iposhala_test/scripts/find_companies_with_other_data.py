from iposhala_test.scripts.mongo import ipo_past_master

def check_other_data():
    # Fields to check under nse_company
    fields = [
        "corporate_announcements",
        "corporate_actions",
        "board_meetings",
        "event_calendar",
        "annual_reports",
        "brsr_reports"
    ]
    
    print("Checking for Other NSE Data in MongoDB (STRICT VALIDATION)...")
    
    for field in fields:
        # Check for:
        # 1. It is a list and not empty (e.g. shareholding)
        # 2. It is a dict AND has (available=True OR payload is non-empty list)
        
        query = {
            "$or": [
                {f"nse_company.{field}": {"$type": "array", "$ne": []}},
                {f"nse_company.{field}.available": True},
                {f"nse_company.{field}.payload": {"$exists": True, "$ne": []}}
            ]
        }
        
        count = ipo_past_master.count_documents(query)
        print(f"[{field}]: Found {count} companies")
        
        if count > 0:
            # List symbols
            cursor = ipo_past_master.find(query, {"symbol": 1})
            symbols = [doc['symbol'] for doc in cursor]
            print(f"  -> Symbols: {', '.join(symbols[:10])}{'...' if count > 10 else ''}")

if __name__ == "__main__":
    check_other_data()
