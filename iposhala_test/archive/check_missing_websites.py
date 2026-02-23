from iposhala_test.scripts.mongo import ipo_past_master
import sys
import os
sys.path.append(os.getcwd())

query = {
    '$and': [
        {'website': {'$exists': False}}, 
        {'company_website': {'$exists': False}}, 
        {'nse_quote.metadata.companyWebsite': {'$exists': False}},
    ]
}

count = ipo_past_master.count_documents(query)
print(f"Companies missing website: {count}")
