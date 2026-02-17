
from googlesearch import search
import time

companies = [
    "Brandman Retail Limited",
    "Shadowfax Technologies Limited"
]

def test_search():
    for company in companies:
        query = f"{company} official website"
        print(f"Searching for: {query}")
        try:
            # simple search, yielding URLs
            for url in search(query, num_results=3):
                print(f"  Found: {url}")
                break # Just get first result
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    test_search()
