import os, sys
sys.path.append(os.getcwd())
try:
    from iposhala_test.scripts.mongo import ipo_live_upcoming, ipo_past_master
    
    print("LIVE:")
    for doc in ipo_live_upcoming.find({}, {"_id": 0, "company_name": 1, "symbol": 1, "ipo_id": 1}):
        print(doc)
        
    print("PAST with 'avana' in id or symbol:")
    for doc in ipo_past_master.find({"$or": [{"ipo_id": {"$regex": "vana", "$options": "i"}}, {"symbol": {"$regex": "vana", "$options": "i"}}]}, {"_id": 0, "company_name": 1, "symbol": 1, "ipo_id": 1}):
        print(doc)
        
except Exception as e:
    print("Error:", e)
