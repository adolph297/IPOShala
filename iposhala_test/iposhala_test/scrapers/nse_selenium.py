import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager



def get_driver(headless=True, enable_logs=False):
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    # mimic real browser
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )

    # Selenium 4 performance logging
    if enable_logs:
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def extract_quote_json(symbol="TCS"):
    driver = get_driver(headless=False, enable_logs=True)

    try:
        page_url = f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}"
        driver.get(page_url)

        # let JS load + network calls happen
        time.sleep(8)

        logs = driver.get_log("performance")

        target_request_id = None
        target_url = None

        # find requestId for getSymbolData call
        for entry in logs:
            msg = json.loads(entry["message"])["message"]

            if msg.get("method") == "Network.responseReceived":
                response = msg["params"]["response"]
                response_url = response.get("url", "")

                if "GetQuoteApi" in response_url and "functionName=getSymbolData" in response_url:
                    target_request_id = msg["params"]["requestId"]
                    target_url = response_url
                    break

        if not target_request_id:
            print("❌ Could not find getSymbolData response in network logs")
            return None

        print("✅ Found quote API URL:", target_url)

        # extract response JSON body from chrome devtools protocol
        body = driver.execute_cdp_cmd(
            "Network.getResponseBody",
            {"requestId": target_request_id}
        )

        data = body.get("body", "")

        try:
            data_json = json.loads(data)
        except Exception:
            data_json = {"raw": data}

        print("✅ Quote JSON extracted successfully")
        return data_json

    finally:
        driver.quit()

def normalize_nse_quote(nse_json):
    try:
        item = nse_json["equityResponse"][0]

        md = item.get("metaData", {})
        ti = item.get("tradeInfo", {})
        ob = item.get("orderBook", {})

        return {
            "symbol": md.get("symbol"),
            "identifier": md.get("identifier"),
            "companyName": md.get("companyName"),

            "lastPrice": ob.get("lastPrice") or md.get("lastPrice") or ti.get("lastPrice"),
            "change": md.get("change"),
            "pChange": md.get("pChange"),

            "open": md.get("open"),
            "high": md.get("dayHigh"),
            "low": md.get("dayLow"),
            "previousClose": md.get("previousClose"),
            "averagePrice": md.get("averagePrice"),

            "volume": ti.get("totalTradedVolume"),
            "value": ti.get("totalTradedValue"),

            "asOf": ti.get("secwisedelposdate")
        }

    except Exception as e:
        return {"error": str(e), "raw": nse_json}


if __name__ == "__main__":
    raw = extract_quote_json("TCS")
    normalized = normalize_nse_quote(raw)
    print(json.dumps(normalized, indent=2))



   