import json
import os
from pymongo import MongoClient
import argparse

# MongoDB connection (Default to the one in other scripts)
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://doadmin:485093A7X1wL2GvS@NX-REPO-DB-0761394b.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
DB_NAME = os.getenv("DB_NAME", "ipo_shala")

def upload_financials(json_file):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db["ipo_past_master"]
        
        # Test connection
        client.admin.command('ping')
        print("Connected to MongoDB successfully.")
        
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        print(f"Loaded {len(data)} records from {json_file}")
        
        updated_count = 0
        for symbol, info in data.items():
            financials = info.get('audited_financials', [])
            website = info.get('website')
            
            if financials:
                # Update database
                result = collection.update_one(
                    {"symbol": symbol},
                    {
                        "$set": {
                            "company_website": website, # Ensure website is also updated
                            "nse_company.audited_financials": financials,
                            "last_discovery_audited": info.get('last_discovery_audited')
                        }
                    }
                )
                
                if result.modified_count > 0:
                    print(f"Updated {symbol}: {len(financials)} reports")
                    updated_count += 1
                else:
                    print(f"Skipped {symbol}: No changes or symbol not found")
            else:
                print(f"Skipping {symbol}: No financials to upload")
                
        print(f"\nUpload complete. Updated {updated_count} companies.")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Please check your internet connection or VPN settings.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="batch_5_financials.json", help="Path to JSON file with financial data")
    args = parser.parse_args()
    
    upload_financials(args.file)
