
from mongo import ipo_past_master
import pprint

print(">>> Searching for populated nse_company data <<<")

# Find a document where announcements payload is not empty
doc = ipo_past_master.find_one({
    "nse_company.announcements.payload": {"$exists": True, "$not": {"$size": 0}}
})

if doc:
    symbol = doc.get('symbol')
    print(f"Found symbol with announcements: {symbol}")
    # Show a bit of the announcements
    pprint.pprint(doc['nse_company']['announcements']['payload'][:2])
else:
    print("No documents found with non-empty announcements payload.")
    
    # Try searching for corporate actions
    doc = ipo_past_master.find_one({
        "nse_company.corporate_actions": {"$exists": True, "$not": {"$size": 0}}
    })
    
    if doc:
        symbol = doc.get('symbol')
        print(f"Found symbol with corporate actions: {symbol}")
        pprint.pprint(doc['nse_company']['corporate_actions'][:2])
    else:
        print("No documents found with non-empty corporate actions.")

# If still nothing, just show symbols that have nse_company.announcements
if not doc:
    c = ipo_past_master.count_documents({"nse_company.announcements": {"$exists": True}})
    print(f"Total documents with nse_company.announcements: {c}")
