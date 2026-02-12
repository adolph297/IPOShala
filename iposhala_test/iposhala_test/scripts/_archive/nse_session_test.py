import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_nse_session():
    session = requests.Session()
    response = session.get(
        "https://www.nseindia.com",
        headers=HEADERS,
        timeout=10
    )
    print("Homepage status:", response.status_code)
    return session

if __name__ == "__main__":
    s = get_nse_session()
    print("Session created successfully")
