import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www.pinelabs.com"
print(f"Fetching {url}...")

try:
    res = requests.get(url, verify=False, timeout=10)
    print(f"Status: {res.status_code}")
    soup = BeautifulSoup(res.text, 'html.parser')
    
    links = soup.find_all('a', href=True)
    print(f"Found {len(links)} links.")
    
    print("\n--- Links with 'investor', 'financial', 'report', 'annual' ---")
    for l in links:
        txt = l.get_text().strip().lower()
        href = l['href']
        if any(k in txt for k in ['investor', 'financial', 'report', 'annual']):
            print(f"Text: {l.get_text().strip()} | Href: {href}")

except Exception as e:
    print(f"Error: {e}")
