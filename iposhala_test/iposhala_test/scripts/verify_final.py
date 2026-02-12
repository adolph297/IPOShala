
from pymongo import MongoClient
import os
import pprint

c = MongoClient('mongodb://localhost:27017')
db = c['iposhala']

print(">>> DIRECT DB VERIFICATION <<<")
doc = db.ipo_past_master.find_one({'symbol': 'E2ERAIL'})
if doc:
    print(f"Symbol: {doc.get('symbol')}")
    print(f"Updated At: {doc.get('nse_company_updated_at')}")
    nse = doc.get('nse_company', {})
    print(f"Sections in nse_company: {list(nse.keys())}")
    
    ann = nse.get('announcements', {})
    payload = []
    if isinstance(ann, dict): payload = ann.get('payload', [])
    elif isinstance(ann, list): payload = ann
    
    print(f"Announcements Count: {len(payload)}")
    if len(payload) > 0:
        print("First announcement preview:")
        pprint.pprint(payload[0])
    
    # Check ipo_master too
    doc_m = db.ipo_master.find_one({'symbol': 'E2ERAIL'})
    print(f"Exists in ipo_master: {doc_m is not None}")
else:
    print("E2ERAIL NOT FOUND in ipo_past_master")
