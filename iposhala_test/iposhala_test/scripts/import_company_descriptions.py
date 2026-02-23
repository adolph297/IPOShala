import os
import pandas as pd
from pymongo import UpdateOne
from iposhala_test.scripts.mongo import ipo_past_master
import re

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, "data", "company_descriptions_final_ai_updated.csv")

def clean_description(desc):
    """Clean up unwanted technical strings or garbage from the description"""
    if not isinstance(desc, str):
        return ""
    
    # Remove Next.js hydration strings like self.__next_f.push(...)
    desc = re.sub(r'self\.__next_f\.push\(.*?\)', '', desc, flags=re.DOTALL)
    
    # Remove escaped quotes and other artifacts
    desc = desc.replace('\\"', '"').replace('\\n', '\n')
    
    # Remove common filler from specific scraping artifacts
    desc = re.sub(r'\[["\d:]+\[.*', '', desc) # Remove trailing bracket junk
    
    # Final cleanup of whitespace
    return desc.strip()

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"CSV file not found: {INPUT_CSV}")
        return

    print(f"Reading {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    
    ops = []
    count = 0
    
    for _, row in df.iterrows():
        symbol = str(row['Symbol']).strip()
        desc = str(row['description'])
        
        if not symbol or symbol == 'nan':
            continue
            
        cleaned_desc = clean_description(desc)
        if not cleaned_desc:
            continue
            
        # Update matching by symbol
        ops.append(
            UpdateOne(
                {"symbol": symbol},
                {"$set": {"description": cleaned_desc}}
            )
        )
        count += 1

    if ops:
        print(f"Updating {len(ops)} documents in ipo_past_master...")
        result = ipo_past_master.bulk_write(ops)
        print(f"Success! Matched: {result.matched_count}, Modified: {result.modified_count}")
    else:
        print("No updates to perform.")

if __name__ == "__main__":
    main()
