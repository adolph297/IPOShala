import requests
from bs4 import BeautifulSoup
import re
import urllib3
import json
import time
from datetime import datetime
from mass_website_discovery import search_website

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

from iposhala_test.scripts.mongo import ipo_past_master
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

# Fallback WEBSITES if DB fails or for testing
WEBSITES = {
    "EXCELSOFT": "https://www.excelsoftcorp.com",
    "CAPILLARY": "https://www.capillarytech.com",
    "FUJIYAMA": "https://www.utlsolarfujiyama.com",
    "TENNECO": "https://www.tennecoindia.com",
    "EMMVEE": "https://www.emmvee.com",
    "PW": "https://www.pw.live",
    "PINELABS": "https://www.pinelabs.com",
    "CURIS": "https://www.curisls.com",
    "FINBUD": "https://www.financebuddha.com",
    "BBGV": "https://groww.in",
    "SHREEJI": "https://www.shreejifmcg.com",
    "LENSKART": "https://www.lenskart.com",
    "STUDDS": "https://www.studds.com",
    "ORKLA": "https://www.orklaindia.com",
    "JLL": "https://www.jayeshlogistics.com",
    "SMC": "https://www.smcindiaonline.com",
    "MIDWEST": "https://www.midwest.in",
    "CANARAHSBC": "https://www.canarahsbclife.com",
    "RUBICON": "https://www.rubicon.co.in",
    "CRAMC": "https://www.canararobeco.com",
    "LGEIL": "https://www.lg.com/in",
    "ANANTAM": "https://www.anantamhighways.com",
    "TATACAP": "https://www.tatacapital.com",
    "SURATMUNI": "https://www.suratmunicipal.gov.in",
    "WEWORK": "https://wework.co.in",
    "MUNISH": "https://www.munishforge.com",
    "BAGDIGITAL": "https://www.bagconvergence.in",
    "SHEEL": "https://www.sheelbiotech.com",
    "GREENLEAF": "https://www.greenleafenvirotech.in",
    "GLOTTIS": "https://www.glottislogistics.in",
    "FABTECH": "https://www.fabtechnologies.com",
    "VIJAYPD": "http://www.vijaypdceutical.com",
    "SUBAHOTELS": "https://www.subahotels.com",
    "MPEL": "https://www.manaspolymers.com",
    "TRUALT": "https://www.trualtbioenergy.com",
    "JAINREC": "https://www.jainmetalgroup.com",
    "EPACKPEB": "http://www.epackprefab.com",
    "BMWVENTLTD": "https://www.bmwventures.com",
    "GURUNANAK": "https://www.gnagro.com",
    "ARSSBL": "https://www.anandrathi.com",
    "STYL": "https://www.seshaasai.com",
    "SOLARWORLD": "https://www.worldsolar.in",
    "JARO": "https://www.jaroeducation.com",
    "ECOLINE": "https://www.ecoline.net.in",
    "MGSL": "https://www.matrix-geo.com",
    "GANESHCP": "https://ganesh.co.in",
    "ATLANTAELE": "https://www.aetrafo.com",
    "PRIMECAB": "https://www.primecabindia.com",
    "SAATVIK": "https://www.saatvikgroup.com",
    "GKENERGY": "https://www.gkenergy.in",
    "SIDDHICOTS": "https://www.siddhicotspin.com",
    "IVALUE": "https://www.ivalue.co.in",
    "VMSTMT": "https://www.vmstmt.com",
    "EUROPRATIK": "https://www.europratik.com",
    "TECHD": "https://www.techdefencelabs.com",
    "URBANCO": "https://www.urbancompany.com",
    "SHRINGARMS": "https://www.shringar.ms",
    "DEVX": "https://devx.work",
    "GML": "https://galaxy.in",
    "TAURIAN": "https://www.taurianmps.com",
    "VIGOR": "https://vigorplastindia.com",
    "OPTIVALUE": "https://optivaluetek.com",
    "AMANTA": "https://amanta.co.in",
    "SNEHAA": "https://www.snehaaorganics.com",
    "VIKRAN": "https://www.vikrangroup.com",
    "AHCL": "https://www.anlon.in",
    "CURRENT": "http://www.currentinfra.com",
    "SATTVAENGG": "https://sattvaengg.in",
    "ANONDITA": "https://www.anonditamedicare.com",
    "SHIVASHRIT": "https://www.shivashritfoods.com",
    "CLASSICEIL": "https://classicelectrodes.com",
    "ARCIIL": "https://www.arcinsulations.com",
    "MEIL": "https://mangals.com",
    "VIKRAMSOLR": "https://www.vikramsolar.com",
    "SHREEJISPG": "https://shreejishipping.in",
    "GEMAROMA": "https://gemaromatics.in",
    "PATELRMART": "https://patelrpl.in",
    "STUDIOLSD": "https://www.studiolsd.in",
    "REGAAL": "https://regaal.in",
    "MRIL": "https://www.mripl.net",
    "BLUESTONE": "https://www.bluestone.com",
    "AMCL": "https://anbmetalcast.com",
    "MEDISTEP": "http://www.medistephc.com",
    "JSWCEMENT": "https://www.jswcement.in",
    "ALLTIME": "https://www.alltimeplastics.com",
    "CONNPLEX": "https://www.theconnplex.com",
    "SAWALIYA": "https://sawaliyafood.com",
    "KRT": "https://www.knowledgerealtytrust.com",
    "HILINFRA": "https://www.highwayinfrastructure.in",
    "BHADORA": "https://www.vidhutcables.com",
    "AARADHYA": "https://aaradhyadisposalindustries.co.in",
    "PARTH": "https://parthelectricals.in",
    "JYOTIGLOBL": "https://jyotiglobalplast.com",
    "FLYSBS": "https://www.sbsaviation.in",
    "RNPL": "https://www.renolpolychem.com",
    "CUDML": "https://www.cashurdrive.com",
    "NSDL": "https://nsdl.co.in",
    "MBEL": "https://mbel.in",
    "LOTUSDEV": "https://lotusdevelopers.com",
    "CPPLUS": "https://www.cpplusworld.com",
}

def get_companies_from_db(limit=None):
   print("Fetching companies from MongoDB...")
   query = {
       "security_type": {"$in": ["EQ", "SME", "BE"]}
   }
   cursor = ipo_past_master.find(query, {"symbol": 1, "website": 1, "company_name": 1})
   if limit:
       cursor = cursor.limit(limit)
   companies = {}
   for doc in cursor:
       symbol = doc.get('symbol')
       if symbol:
           companies[symbol] = doc.get('website')
   print(f"Fetched {len(companies)} companies from DB.")
   return companies

def get_base_url(url):
    parts = url.split("/")
    return "/".join(parts[:3])

def extract_financials(symbol, website):
    print(f"Scanning {symbol} at {website}...")
    
    discovery_urls = [website.rstrip('/') + "/"]
    common_paths = [
        "investors", "investor-relations", "financial-information", 
        "annual-reports", "web/annual_reports", "web/investors",
        "investor-information", "investor-relations/financials",
        "about-us/investor-relations"
    ]
    for p in common_paths:
        discovery_urls.append(website.rstrip('/') + "/" + p)

    found_reports = []
    checked_urls = set()

    for url in discovery_urls:
        if url in checked_urls: continue
        checked_urls.add(url)
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=10, verify=False)
            if res.status_code != 200: continue
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 1. Crawl for sub-links
            if url == discovery_urls[0]:
                links = soup.find_all('a', href=True)
                for l in links:
                    ltext = l.get_text().lower()
                    lhref = l['href']
                    if any(k in ltext for k in ["investor", "annual", "report", "financial"]):
                        if not lhref.startswith('http'):
                            lhref = get_base_url(website) + "/" + lhref.lstrip('/')
                        if lhref not in checked_urls:
                            discovery_urls.append(lhref)

            # 2. Extract PDFs
            # Method A: Direct link text
            plinks = soup.find_all('a', href=True)
            for l in plinks:
                ltext = l.get_text().strip()
                lhref = l['href']
                
                if "Annual Report" in ltext or "Audited" in ltext:
                    year_match = re.search(r'(\d{4}-\d{2,4})', ltext)
                    if year_match and (".pdf" in lhref.lower() or "pdf" in ltext.lower() or "View" in ltext):
                        year = year_match.group(1)
                        full_url = lhref
                        if not full_url.startswith('http'):
                            full_url = get_base_url(url) + "/" + full_url.lstrip('/')
                        
                        found_reports.append({
                            "year": year,
                            "url": full_url,
                            "type": "Annual Report",
                            "period": "Annual"
                        })

            # Method B: Sibling structure
            all_text_nodes = soup.find_all(string=re.compile(r'Annual Report', re.I))
            for node in all_text_nodes:
                parent = node.parent
                container = parent
                for _ in range(3):
                    link = container.find('a', href=True) if container else None
                    if link and ".pdf" in link['href'].lower():
                        ltext = node.strip()
                        lhref = link['href']
                        year_match = re.search(r'(\d{4}[-–—]\d{2,4})', ltext)
                        if year_match:
                            year = year_match.group(1)
                            full_url = lhref
                            if not full_url.startswith('http'):
                                full_url = get_base_url(url) + "/" + full_url.lstrip('/')
                            
                            found_reports.append({
                                "year": year,
                                "url": full_url,
                                "type": "Annual Report",
                                "period": "Annual"
                            })
                            break
                    container = container.parent if container else None
                    if not container: break

            # 2b. Extract Quarterly / Financial Results
            qlinks = soup.find_all('a', href=True)
            for l in qlinks:
                ltext = l.get_text().strip()
                lhref = l['href']
                
                # Keywords for Quarterly / Financial Results
                if any(k in ltext.lower() for k in ["quarter", "financial result", "unaudited", "q1", "q2", "q3", "q4"]):
                     # Exclude if it's likely an Annual Report (already handled)
                    if "annual report" in ltext.lower():
                        continue
                        
                    # Basic validation
                    if ".pdf" in lhref.lower() or "pdf" in ltext.lower() or "view" in ltext.lower():
                        full_url = lhref
                        if not full_url.startswith('http'):
                            full_url = get_base_url(url) + "/" + full_url.lstrip('/')
                        
                        # Create a label
                        label = ltext
                        if len(label) > 50:
                            label = label[:47] + "..."
                        
                        # Clean up label
                        label = re.sub(r'\s+', ' ', label).strip()

                        # Attempt to extract a date or year if possible, otherwise use current year/date
                        
                        # Check for year pattern
                        year_match = re.search(r'(\d{4}[-–—]\d{2,4})', ltext)
                        year = year_match.group(1) if year_match else None
                        
                        found_reports.append({
                            "url": full_url,
                            "type": "Financial Result",
                            "label": label,
                            "year": year, 
                            "period": "Quarterly" if "quarter" in ltext.lower() or any(q in ltext.lower() for q in ["q1","q2","q3","q4"]) else "Other"
                        })

        except Exception as e:
            print(f"  Error scanning {url}: {e}")

    # Deduplicate based on URL
    unique_reports = {}
    
    # Merge extracted quarterly results into unique_reports (Wait, found_reports has Annual Reports, quarterly_reports has Quarterly)
    # Actually, I should have appended to a list or dict.
    # Let's fix the structure.
    # I'll modify the loop to append found items to `found_reports` list, but with different types.
    
    # NO, I will just copy the logic above but append to found_reports directly.

    


    # Merge Annual Reports into the unique_reports dict
    for r in found_reports:
        # Create a label for Annual Reports if not exists
        if "label" not in r:
            r["label"] = f"Annual Report {r['year']}"
        
        # Use URL as ID to deduplicate
        if r['url'] not in unique_reports:
            unique_reports[r['url']] = r

    final_list = list(unique_reports.values())
    
    # Sort: Annual Reports first (by year desc), then others
    def sort_key(x):
        # Primary sort: Year (descending)
        y = x.get("year")
        if y:
            # Try to normalize year to start year for sorting
            # e.g. 2023-24 -> 2023
            try:
                y_start = int(y.split('-')[0])
                return (1, y_start)
            except:
                return (0, 0)
        return (0, 0)

    final_list.sort(key=sort_key, reverse=True)
    
    return final_list

def main():
    all_financials = {}

    # Load existing if available
    if os.path.exists('batch_5_financials.json'):
        try:
            with open('batch_5_financials.json', 'r') as f:
                all_financials = json.load(f)
            print(f"Loaded {len(all_financials)} existing records from batch_5_financials.json")
        except:
             print("Could not load existing file, starting fresh.")
    
    # Merge DB companies with hardcoded ones (DB takes precedence if we want, or just use DB)
    # Let's use DB primarily, and fall back to hardcoded if DB is empty
    db_websites = get_companies_from_db(limit=None)
    if db_websites:
        target_websites = db_websites
    else:
        target_websites = WEBSITES

    total = len(target_websites)
    for idx, (symbol, website) in enumerate(target_websites.items()):
        if symbol in all_financials:
             print(f"[{idx+1}/{total}] Skipping {symbol}, already processed.")
             continue

        print(f"[{idx+1}/{total}] Processing {symbol}...")
        
        # Dynamic discovery if website is missing or placeholder
        if not website or website == "https://www.google.com":
             print(f"  Website missing for {symbol}. Attempting discovery...")
             found_url = search_website(symbol)
             if found_url:
                 website = found_url
                 print(f"  Discovered: {website}")
             else:
                 print(f"  Could not find website for {symbol}. Skipping.")
                 continue

        try:
            reports = extract_financials(symbol, website)
            if reports:
                print(f"  Found {len(reports)} reports for {symbol}")
                all_financials[symbol] = {
                    "website": website,
                    "audited_financials": reports,
                    "last_discovery_audited": datetime.now().isoformat()
                }
            else:
                print(f"  No reports found for {symbol}")
        except Exception as e:
            print(f"  Critical error for {symbol}: {e}")

        # Save every 5 iterations or at the end
        if (idx + 1) % 5 == 0 or (idx + 1) == total:
            print(f"Saving progress at {idx+1}/{total}...")
            with open('batch_5_financials.json', 'w') as f:
                json.dump(all_financials, f, indent=2)
            
    print("\nExtraction complete. Saved to batch_5_financials.json")

if __name__ == "__main__":
    main()
