
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from iposhala_test.scripts.mongo import ipo_past_master

def get_names():
    symbols = ['MUKTI', 'GLOBAL', 'MAHALAXMI', 'SSOVERSEAS']
    print(f"Querying for {symbols}...")
    cursor = ipo_past_master.find({'symbol': {'$in': symbols}}, {'symbol': 1, 'company_name': 1})
    for doc in cursor:
        print(f"Symbol: {doc.get('symbol')} -> Name: {doc.get('company_name')}")

if __name__ == "__main__":
    get_names()
