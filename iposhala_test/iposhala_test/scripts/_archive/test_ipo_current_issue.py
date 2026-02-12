import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_nse_session():
    s = requests.Session()
    r = s.get("https://www.nseindia.com", headers=HEADERS, timeout=10)
    print("Homepage status:", r.status_code)
    return s

if __name__ == "__main__":
    session = get_nse_session()

    url = "https://www.nseindia.com/api/ipo-current-issue"
    resp = session.get(url, headers=HEADERS, timeout=10)

    print("API status:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("Preview:", resp.text[:200])

