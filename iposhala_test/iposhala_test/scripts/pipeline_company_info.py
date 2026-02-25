import os
import json
import logging
import requests
import re
import argparse
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import local
from dotenv import load_dotenv

# Add project root to path
import sys
sys.path.append(os.getcwd())
from iposhala_test.scripts.mongo import ipo_past_master
from iposhala_test.scrapers.nse_company_dynamic import selenium_fetch_shareholding_pattern

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load ENV for descriptions
load_dotenv(os.path.join(os.getcwd(), ".env"))
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "").strip()

# ==========================================
# LOGO ENGINE
# ==========================================
def is_valid_logo(url):
    if not url: return False
    ext = os.path.splitext(urlparse(url).path)[1].lower()
    return ext in ['.png', '.jpg', '.jpeg', '.svg', '.webp', '.ico']

def is_blacklisted_image(url, text):
    combined = (url + " " + text).lower()
    blacklist = ["banner", "slide", "product", "pack", "bg", "background", "hero", "item", "gallery", "advertisement", "ad-", "promo", "offer", "thumbnail", "avatar", "profile", "social", "youtube", "placeholder", "pixel", "blank", "spacer", "logohere"]
    return any(b in combined for b in blacklist)

def find_chittorgarh_logo(company_name, symbol=None):
    try:
        name = re.split(r'[-—(]', company_name.lower())[0].strip()
        full_slug = name.replace(" ", "-").replace(".", "").replace("&", "n")
        stripped_name = name
        suffixes = [" limited", " ltd", " plc", " corp", " corporation", " inc"]
        for suffix in suffixes:
            if stripped_name.endswith(suffix):
                stripped_name = stripped_name[:len(stripped_name)-len(suffix)]
                break 
        stripped_slug = stripped_name.strip().replace(" ", "-").replace(".", "").replace("&", "n")
        
        slugs = {full_slug, stripped_slug}
        if symbol:
            sym = symbol.upper().strip()
            if len(sym) >= 3:
                slugs.add(sym.lower())
                slugs.add(re.sub(r'[0-9]+$', '', sym).lower())
                
        final_slugs = {s.strip().replace(" ", "-").replace(".", "").replace("&", "n") for s in slugs if s}
        possible_urls = []
        for s in final_slugs:
            s = s.strip("-")
            if len(s) < 2: continue
            possible_urls.extend([
                f"https://www.chittorgarh.net/images/ipo/{s}-logo.png",
                f"https://www.chittorgarh.com/images/ipo/{s}-logo.png",
                f"https://www.chittorgarh.net/images/ipo/{s}-limited-logo.png",
                f"https://www.chittorgarh.net/images/ipo/{s}-ltd-logo.png"
            ])
            
        seen = set()
        dedup_urls = [x for x in possible_urls if not (x in seen or seen.add(x))]

        for url in dedup_urls:
            try:
                if requests.head(url, timeout=5, verify=False).status_code == 200:
                    return url
            except: continue
    except: pass
    return None

def find_clearbit_logo(website_url):
    try:
        domain = urlparse(website_url).netloc.replace("www.", "")
        url = f"https://logo.clearbit.com/{domain}"
        if requests.head(url, timeout=5).status_code == 200:
            return url
    except: pass
    return None

def find_logo(website_url, company_name=None, symbol=None):
    if not website_url: return None
    try:
        response = requests.get(website_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            candidates = []
            
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                full_url = urljoin(website_url, og_image["content"])
                if is_valid_logo(full_url) and not is_blacklisted_image(full_url, ""):
                    candidates.append({"url": full_url, "score": 60})
                    
            for img in soup.find_all("img"):
                src = img.get("src")
                if not src: continue
                alt, cls, img_id = (img.get("alt") or "").lower(), " ".join(img.get("class") or []).lower(), (img.get("id") or "").lower()
                score = 80 if any("logo" in x for x in [alt, cls, img_id]) else 0
                if "logo" in src.lower(): score = max(score, 85)
                if score > 0:
                    full_url = urljoin(website_url, src)
                    if is_valid_logo(full_url) and not is_blacklisted_image(full_url, alt):
                        candidates.append({"url": full_url, "score": score})
                        
            if candidates:
                candidates.sort(key=lambda x: x['score'], reverse=True)
                if candidates[0]['score'] < 80 and company_name:
                    ch_logo = find_chittorgarh_logo(company_name, symbol)
                    if ch_logo: return ch_logo
                return candidates[0]['url']
    except: pass
    if company_name:
        ch_logo = find_chittorgarh_logo(company_name, symbol)
        if ch_logo: return ch_logo
    return find_clearbit_logo(website_url)

def fetch_and_save_logos(limit=50, symbol=None, force=False):
    query = {} if force else {"$or": [{"logo_url": {"$exists": False}}, {"logo_url": None}]}
    if symbol: query["symbol"] = symbol
    companies = list(ipo_past_master.find(query).limit(limit))
    logging.info(f"[LOGOS] Found {len(companies)} candidates")
    
    for comp in companies:
        sym, name, web = comp['symbol'], comp.get('company_name', comp['symbol']), comp.get('website')
        logo = find_logo(web, name, sym) if web else find_chittorgarh_logo(name, sym)
        if logo:
            logging.info(f"  [LOGOS] Found for {sym}: {logo}")
            ipo_past_master.update_one({"symbol": sym}, {"$set": {"logo_url": logo}})

# ==========================================
# DESCRIPTIONS ENGINE
# ==========================================
_thread = local()
def get_session():
    if not hasattr(_thread, "session"):
        s = requests.Session()
        s.headers.update({"User-Agent": "Mozilla/5.0"})
        _thread.session = s
    return _thread.session

def fetch_company_desc(company_name):
    if not SERPER_API_KEY: return ""
    try:
        res = requests.post("https://google.serper.dev/search", 
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": f'"{company_name}" (IPO OR "about company" OR profile) (site:moneycontrol.com OR site:chittorgarh.com)', "num": 5}, timeout=10)
        links = [item["link"] for item in res.json().get("organic", []) if "link" in item]
        for url in links:
            html = get_session().get(url, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
            paras = sorted(set([re.sub(r"\s+", " ", p.get_text(" ", strip=True)) for p in soup.find_all("p") if len(p.get_text()) > 80]), key=len, reverse=True)
            if paras: return " ".join(paras[:2])
    except: pass
    return ""

def generate_and_save_descriptions(limit=50, symbol=None, force=False):
    if not SERPER_API_KEY:
        logging.warning("[DESCRIPTIONS] SERPER_API_KEY missing. Skipping descriptions.")
        return
    query = {} if force else {"$or": [{"description": {"$exists": False}}, {"description": ""}]}
    if symbol: query["symbol"] = symbol
    companies = list(ipo_past_master.find(query).limit(limit))
    logging.info(f"[DESCRIPTIONS] Found {len(companies)} candidates")

    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(fetch_company_desc, c.get('company_name', c['symbol'])): c for c in companies}
        for future in as_completed(futures):
            comp = futures[future]
            try:
                desc = future.result()
                if desc:
                    logging.info(f"  [DESCRIPTIONS] Found for {comp['symbol']} ({len(desc)} chars)")
                    ipo_past_master.update_one({"symbol": comp['symbol']}, {"$set": {"description": desc}})
            except: pass

# ==========================================
# SHAREHOLDING ENGINE
# ==========================================
def fetch_and_save_shareholding(limit=50, symbol=None, force=False):
    query = {} if force else {"nse_company.shareholding_patterns": {"$exists": False}}
    if symbol: query["symbol"] = symbol
    companies = list(ipo_past_master.find(query).limit(limit))
    logging.info(f"[SHAREHOLDING] Found {len(companies)} candidates")
    
    for count, comp in enumerate(companies):
        sym = comp['symbol']
        try:
            res = selenium_fetch_shareholding_pattern(sym)
            if res.get('__available__') and isinstance(res.get('data'), list) and res['data']:
                parsed = [{"period": e.get('date'), "promoter": float(e.get('pr_and_prgrp') or 0), "public": float(e.get('public_val') or 0)} for e in res['data'] if e.get('date')]
                if parsed:
                    ipo_past_master.update_one({"symbol": sym}, {"$set": {"nse_company.shareholding_patterns": parsed}})
                    logging.info(f"  [SHAREHOLDING] Saved {len(parsed)} records for {sym}")
            time.sleep(1)
        except Exception as e:
            logging.error(f"  [SHAREHOLDING] Failed for {sym}: {str(e)}")

# ==========================================
# CLI ROUTER
# ==========================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--logos", action="store_true")
    parser.add_argument("--desc", action="store_true")
    parser.add_argument("--shares", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--symbol", type=str)
    args = parser.parse_args()

    if args.all or args.logos: fetch_and_save_logos(args.limit, args.symbol, args.force)
    if args.all or args.desc: generate_and_save_descriptions(args.limit, args.symbol, args.force)
    if args.all or args.shares: fetch_and_save_shareholding(args.limit, args.symbol, args.force)
    
    if not any([args.all, args.logos, args.desc, args.shares]):
        logging.info("Please specify a flag: --logos, --desc, --shares, or --all")

if __name__ == "__main__":
    main()
