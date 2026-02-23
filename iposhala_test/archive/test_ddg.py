from ddgs import DDGS
import logging
logging.basicConfig(level=logging.INFO)

print("Starting DDGS test...")
try:
    with DDGS() as ddgs:
        results = list(ddgs.text("python programming", max_results=3, backend='lite'))
        print(f"Found {len(results)} results.")
        for r in results:
            print(f"- {r['title']} ({r['href']})")
except Exception as e:
    print(f"Error: {e}")
print("Test complete.")
