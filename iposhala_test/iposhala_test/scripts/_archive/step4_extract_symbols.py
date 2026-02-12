import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_nse_session():
    s = requests.Session()
    s.get("https://www.nseindia.com", headers=HEADERS, timeout=10)
    return s

if __name__ == "__main__":
    session = get_nse_session()

    url = "https://www.nseindia.com/api/ipo-current-issue"
    response = session.get(url, headers=HEADERS, timeout=10)

    data = response.json()

    print("Total current IPOs:", len(data))
    print("Symbols:")

    for ipo in data:
        print("-", ipo.get("symbol"), "|", ipo.get("companyName"))
