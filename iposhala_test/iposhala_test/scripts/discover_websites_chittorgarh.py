import requests
from bs4 import BeautifulSoup
import re
import argparse
from iposhala_test.scripts.mongo import ipo_past_master
import time

def search_chittorgarh_for_website(company_name):
    # Search query specifically targeting chittorgarh
    search_query = f"{company_name} IPO contact details site:chittorgarh.com"
    print(f"Searching for: {search_query}")
    
    # Use a simple search via Google/Bing search tool or just try to find the URL
    # For this script, we'll use a mocked search or a real web search tool if available.
    # Since I'm an agent, I can use the search_web tool in the main loop.
    # But for a STANDALONE script, I'll need a way to find the page.
    
    # Strategy: Find the Chittorgarh IPO link from the search results
    from iposhala_test.scripts.mongo import ipo_past_master
    
    # We'll use a search tool call in the EXECUTION phase to get the URL
    pass

def extract_website_from_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=15, verify=False)
        if res.status_code != 200:
            print(f"Error: Status {res.status_code} for {url}")
            return None
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Target "Contact Details" section specifically
        contact_section = None
        # Look for the header "Contact Details"
        headers_found = soup.find_all(['h2', 'h3', 'b', 'strong', 'span'])
        for h in headers_found:
            if "Contact Details" in h.get_text():
                contact_section = h
                break
        
        if contact_section:
            # Look at subsequent elements for the "Visit Website" link
            next_node = contact_section
            # Scan next siblings for up to 20 elements or until next section header
            for _ in range(30):
                next_node = next_node.next_element
                if not next_node: break
                
                if next_node.name == 'a' and next_node.has_attr('href'):
                    if "Visit Website" in next_node.get_text():
                        website_url = next_node['href']
                        if "chittorgarh.com" not in website_url:
                            return website_url
                
                # If we encounter another major header, stop
                if next_node.name in ['h2', 'h3'] and "Contact Details" not in next_node.get_text():
                    # Check if we already found it in this stretch
                    pass

        # Fallback to the original logic but skip the first few if they are registrar/lead manager
        # (Though that's brittle, targeting the section is better)
        
    except Exception as e:
        print(f"Error extracting from {url}: {e}")
    return None

def update_company_website(symbol, website_url):
    if not website_url:
        return False
    
    result = ipo_past_master.update_one(
        {"symbol": symbol},
        {"$set": {"website": website_url, "website_source": "chittorgarh"}}
    )
    return result.modified_count > 0

def process_symbol(symbol, chittorgarh_url):
    print(f"Processing {symbol} via {chittorgarh_url}...")
    website = extract_website_from_page(chittorgarh_url)
    if website:
        if update_company_website(symbol, website):
            print(f"  Success: Updated {symbol} -> {website}")
            return True
        else:
            print(f"  Info: {symbol} already has this website or update failed.")
    else:
        print(f"  Error: Could not find website on {chittorgarh_url}")
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", help="Company symbol")
    parser.add_argument("--url", help="Chittorgarh IPO page URL")
    args = parser.parse_args()

    if args.symbol and args.url:
        process_symbol(args.symbol, args.url)
    else:
        print("Please provide both --symbol and --url")

if __name__ == "__main__":
    main()
