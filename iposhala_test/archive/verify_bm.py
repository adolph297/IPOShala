from pymongo import MongoClient

def find_bm():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["iposhala"]
    coll = db["ipo_past_master"]
    
    print("Checking for IPOs with Board Meetings...")
    count = 0
    for doc in coll.find({"nse_company.board_meetings": {"$exists": True}}):
        bm = doc.get("nse_company", {}).get("board_meetings", [])
        has_data = False
        
        if isinstance(bm, list) and len(bm) > 0:
            has_data = True
        elif isinstance(bm, dict):
            if bm.get("payload") or bm.get("data") or (isinstance(bm.get("rows"), list) and len(bm["rows"]) > 0):
                has_data = True
        
        if has_data:
            print(f"- {doc.get('symbol', 'UNKNOWN')}")
            count += 1
            if count >= 5: # Just show 5
                break
    
    if count == 0:
        print("No IPOs found with board meetings data.")

if __name__ == "__main__":
    find_bm()
