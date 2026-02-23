
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def list_missing():
    print("Listing missing websites...")
    query = {
        '$and': [
            {'website': {'$exists': False}}, 
            {'company_website': {'$exists': False}}, 
            {'nse_quote.metadata.companyWebsite': {'$exists': False}}
        ]
    }
    cursor = ipo_past_master.find(query, {'symbol': 1, 'company_name': 1}).limit(50)
    for doc in cursor:
        print(f"Symbol: {doc.get('symbol')} -> Name: {doc.get('company_name')}")

if __name__ == "__main__":
    list_missing()
