
import os
import json
import logging
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from iposhala_test.scripts.mongo import ipo_past_master

# Standard timeout for requests
TIMEOUT = 10

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def is_valid_logo(url):
    """Basic check if the URL looks like a logo image."""
    if not url: return False
    ext = os.path.splitext(urlparse(url).path)[1].lower()
    return ext in ['.png', '.jpg', '.jpeg', '.svg', '.webp', '.ico']

def is_blacklisted_image(url, text):
    """Avoid obvious non-logo images like banners, products, etc."""
    combined = (url + " " + text).lower()
    # Expanded blacklist for better filtering
    blacklist = [
        "banner", "slide", "product", "pack", "bg", "background", "hero", 
        "item", "gallery", "advertisement", "ad-", "promo", "offer", 
        "category", "thumbnail", "avatar", "profile", "icon-font", 
        "payment", "card", "facebook", "twitter", "linkedin", "instagram",
        "insta", "follow", "social", "youtube", "whatsapp", "telegram",
        "placeholder", "pixel", "blank", "spacer", "white-logo", "black-logo",
        "customer", "client", "brand-guide", "vector", "pdf-icon", "download-icon",
        "untitled design", "untitled-design", "untitled%20design", "logohere", "your-logo", "path-to-your-logo"
    ]
    return any(b in combined for b in blacklist)

def extract_from_json_ld(soup, base_url):
    """Extract logo candidates from JSON-LD schema blocks."""
    candidates = []
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                # Handle single object or @graph
                items = data.get("@graph", [data])
                for item in items:
                    if not isinstance(item, dict): continue
                    
                    # Look for logo fields in Organization, Brand, Website
                    logo = item.get("logo")
                    if isinstance(logo, dict):
                        logo = logo.get("url")
                    
                    if logo and isinstance(logo, str):
                        full_url = urljoin(base_url, logo)
                        # Skip if it looks like a placeholder or blacklisted
                        if is_blacklisted_image(full_url, ""):
                            continue
                        
                        score = 100
                        # Penalize generic hostnames even more to trigger fallbacks
                        if "wixstatic" in full_url or "wp-content" in full_url or "cdn" in full_url:
                            score = 75 
                            
                        candidates.append({"url": full_url, "score": score, "source": "json-ld"})
        except:
            continue
    return candidates

def find_chittorgarh_logo(company_name, symbol=None):
    """Fallback to Chittorgarh for high-quality IPO logos."""
    try:
        # Clean name for slug
        base_name = company_name.lower()
        # Strip metadata like "-Issue Withdrawn" or "(Mainboard)"
        name = re.split(r'[-—(]', base_name)[0].strip()
        
        # Variation 1: Full name slug (cleaned)
        full_slug = name.replace(" ", "-").replace(".", "").replace("&", "n")
        
        # Variation 2: Stripped suffix slug (Only strip LAST suffix)
        stripped_name = name
        suffixes = [" limited", " ltd", " plc", " corp", " corporation", " inc"]
        for suffix in suffixes:
            if stripped_name.endswith(suffix):
                stripped_name = stripped_name[:len(stripped_name)-len(suffix)]
                break # Only strip one
        stripped_slug = stripped_name.strip().replace(" ", "-").replace(".", "").replace("&", "n")
        
        # Variation 3: Symbol slugs
        symbol_slugs = []
        if symbol:
            sym = symbol.upper().strip()
            if len(sym) >= 3:
                symbol_slugs.append(sym.lower())
                # If symbol ends in numbers (like PFC2026), try without numbers
                sym_no_nums = re.sub(r'[0-9]+$', '', sym)
                if len(sym_no_nums) >= 3:
                    symbol_slugs.append(sym_no_nums.lower())

        slugs = set([full_slug, stripped_slug])
        for s in slugs.copy():
            if s: slugs.add(s.strip("-"))
            
        for s in symbol_slugs: 
            if s: slugs.add(s.lower().replace(" ", "-"))
        
        # Final cleanup: ensure no spaces in any slug
        final_slugs = set()
        for s in slugs:
            if s:
                clean_s = s.strip().replace(" ", "-").replace(".", "").replace("&", "n")
                if len(clean_s) >= 2:
                    final_slugs.add(clean_s)
        
        possible_urls = []
        for s in list(final_slugs):
            s = s.strip("-")
            possible_urls.append(f"https://www.chittorgarh.net/images/ipo/{s}-logo.png")
            possible_urls.append(f"https://www.chittorgarh.com/images/ipo/{s}-logo.png")
            if not any(s.endswith(suff.strip()) for suff in suffixes):
                possible_urls.append(f"https://www.chittorgarh.net/images/ipo/{s}-limited-logo.png")
                possible_urls.append(f"https://www.chittorgarh.net/images/ipo/{s}-ltd-logo.png")
        
        # Deduplicate while preserving order
        seen = set()
        dedup_urls = []
        for url in possible_urls:
            if url not in seen:
                dedup_urls.append(url)
                seen.add(url)

        logging.info(f"    Possible Chittorgarh slugs for {company_name} ({symbol}): {list(final_slugs)}")
        for url in dedup_urls:
            try:
                res = requests.head(url, headers=HEADERS, timeout=5, verify=False)
                if res.status_code == 200:
                    return url
            except: continue
    except: pass
    return None

def find_logo(website_url, company_name=None, symbol=None):
    if not website_url: return None
    
    try:
        response = requests.get(website_url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        if response.status_code != 200: return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        candidates = []

        # 1. JSON-LD Discovery
        json_ld_logos = extract_from_json_ld(soup, website_url)
        candidates.extend(json_ld_logos)

        # 2. Check for favicon/touch icons
        icon_links = soup.find_all("link", rel=lambda x: x and ('icon' in x.lower() or 'apple-touch-icon' in x.lower()))
        for icon in icon_links:
            href = icon.get("href")
            if href:
                full_url = urljoin(website_url, href)
                if is_valid_logo(full_url) and not is_blacklisted_image(full_url, ""):
                    score = 20 # Favicons get low score vs real brand logos
                    if 'apple-touch' in str(icon): score = 25
                    candidates.append({"url": full_url, "score": score, "source": "icon"})

        # 3. Check Open Graph image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            full_url = urljoin(website_url, og_image["content"])
            if is_valid_logo(full_url) and not is_blacklisted_image(full_url, ""):
                candidates.append({"url": full_url, "score": 60, "source": "og"})
                
        # 4. Look for <img> tags in <header> or with "logo" in class/id/alt
        header = soup.find("header") or soup.find("nav")
        search_area = header if header else soup
        
        for img in search_area.find_all("img"):
            src = img.get("src")
            if not src: continue
            
            alt = (img.get("alt") or "").lower()
            cls = " ".join(img.get("class") or []).lower()
            img_id = (img.get("id") or "").lower()
            
            score = 0
            if "logo" in alt or "logo" in cls or "logo" in img_id:
                score = 80
            
            # Boost score if filename itself contains "logo"
            if "logo" in src.lower():
                score = max(score, 85)
                
            if score > 0 and header:
                score += 15 # Extra points if inside header/nav

            if score > 0:
                full_url = urljoin(website_url, src)
                if is_valid_logo(full_url) and not is_blacklisted_image(full_url, alt):
                    candidates.append({"url": full_url, "score": score, "source": "img-tag"})
        
        if candidates:
            candidates.sort(key=lambda x: x['score'], reverse=True)
            best_local = candidates[0]
            
            # If best local is just a favicon or generic source (score < 80), try Chittorgarh
            if best_local['score'] < 80 and company_name:
                logging.info(f"  Attempting Chittorgarh fallback for {company_name} (Best local score: {best_local['score']})")
                ch_logo = find_chittorgarh_logo(company_name, symbol)
                if ch_logo:
                    logging.info(f"  SUCCESS: Using Chittorgarh fallback: {ch_logo}")
                    return ch_logo
                else:
                    logging.info(f"  FAILURE: Chittorgarh fallback returned None for {company_name}")
            
            logging.info(f"  Selected local logo: {best_local['url']} (Score: {best_local['score']})")
            return best_local['url']
        
        # Fallback to Chittorgarh if nothing found on site
        if company_name:
            logging.info(f"  No local candidates. Attempting Chittorgarh fallback for {company_name}")
            return find_chittorgarh_logo(company_name, symbol)

    except Exception as e:
        logging.error(f"Error scanning {website_url}: {e}")
        
    return None

def run_batch(limit=50, force=False, chittorgarh_only=False):
    query = {}
    if not chittorgarh_only:
        query["website"] = {"$exists": True, "$ne": None}
    
    domain_blacklist = ["wikipedia.org", "nseindia.com", "bseindia.com", "moneycontrol.com", "chittorgarh.com"]
    
    if not force:
        query["logo_url"] = {"$exists": False}
        
    companies = list(ipo_past_master.find(query).limit(limit))
    logging.info(f"Found {len(companies)} companies to scan for logos (Force: {force}).")
    
    for comp in companies:
        symbol = comp['symbol']
        website = comp.get('website')
        name = comp.get('company_name', symbol)
        
        if chittorgarh_only:
            logging.info(f"Scanning {symbol} via Chittorgarh only...")
            logo = find_chittorgarh_logo(name, symbol)
        else:
            if not website:
                logging.info(f"Skipping {symbol} - no website and not in chittorgarh-only mode")
                continue
            
            logging.info(f"Scanning {symbol} at {website}...")
            if any(d in website.lower() for d in domain_blacklist):
                # Try Chittorgarh even if website is blacklisted
                logo = find_chittorgarh_logo(name, symbol)
                if logo:
                    logging.info(f"  Found Chittorgarh logo for blacklisted site {symbol}: {logo}")
                    ipo_past_master.update_one({"symbol": symbol}, {"$set": {"logo_url": logo}})
                continue
            logo = find_logo(website, name, symbol)
        
        if logo:
            logging.info(f"  FOUND: {logo}")
            ipo_past_master.update_one(
                {"symbol": symbol},
                {"$set": {"logo_url": logo}}
            )
        else:
            logging.info(f"  No logo found for {symbol}")
            if not force:
                # Mark as attempted
                ipo_past_master.update_one(
                    {"symbol": symbol},
                    {"$set": {"logo_url": None}}
                )

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="IPO Logo Discovery Script")
    parser.add_argument("limit", type=int, nargs="?", default=50, help="Batch limit")
    parser.add_argument("--force", action="store_true", help="Force re-scan even if logo_url exists")
    parser.add_argument("--symbol", type=str, help="Scan a specific symbol")
    parser.add_argument("--chittorgarh-only", action="store_true", help="Only use Chittorgarh for logos")
    
    args = parser.parse_args()
    
    if args.symbol:
        comp = ipo_past_master.find_one({"symbol": args.symbol.upper()})
        if comp:
            name = comp.get('company_name', args.symbol)
            website = comp.get('website', '')
            logging.info(f"Scanning single symbol: {args.symbol} (Name: {name}, Chittorgarh Only: {args.chittorgarh_only})")
            
            if args.chittorgarh_only:
                logo = find_chittorgarh_logo(name, args.symbol.upper())
            else:
                logo = find_logo(website, name, args.symbol.upper()) if website else find_chittorgarh_logo(name, args.symbol.upper())
                
            if logo:
                logging.info(f"  FOUND: {logo}")
                ipo_past_master.update_one({"symbol": comp['symbol']}, {"$set": {"logo_url": logo}})
            else:
                logging.info("  No logo found.")
    else:
        run_batch(args.limit, args.force, args.chittorgarh_only)
