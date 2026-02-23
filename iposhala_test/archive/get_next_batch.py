
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def get_batch(limit=10):
    query = {
        '$and': [
            {'website': {'$exists': False}}, 
            {'company_website': {'$exists': False}}, 
            {'nse_quote.metadata.companyWebsite': {'$exists': False}}
        ]
    }
    cursor = ipo_past_master.find(query, {'symbol': 1, 'company_name': 1}).limit(limit)
    for doc in cursor:
        print(f"{doc.get('symbol')}|{doc.get('company_name')}")

if __name__ == "__main__":
    try:
        limit = int(sys.argv[1])
    except:
        limit = 10
    get_batch(limit)
