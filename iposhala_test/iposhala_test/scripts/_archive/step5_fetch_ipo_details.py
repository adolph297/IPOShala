import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_nse_session():
    session = requests.Session()
    r = session.get("https://www.nseindia.com", headers=HEADERS, timeout=10)
    print("Homepage status:", r.status_code)
    return session

if __name__ == "__main__":
    session = get_nse_session()

    # ✅ USE ONLY A PAST IPO SYMBOL
    symbol = "IDEAFORGE"


    url = f"https://www.nseindia.com/api/ipo-details?symbol={symbol}"
    resp = session.get(url, headers=HEADERS, timeout=10)

    print("Status:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))

    if not resp.headers.get("Content-Type", "").startswith("application/json"):
        print("❌ NSE did not return JSON")
        print(resp.text[:200])
    else:
        data = resp.json()
        documents = data.get("documents", [])

        print("\nDOCUMENTS FOUND:\n")
        for doc in documents:
            print("Title :", doc.get("title"))
            print("URL   :", doc.get("url"))
            print("-" * 50)
