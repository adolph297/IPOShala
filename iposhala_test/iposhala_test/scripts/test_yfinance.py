import yfinance as yf
from datetime import datetime, timedelta

def test_yf(symbol):
    print(f"Testing yfinance for {symbol}...")
    for suffix in [".NS", ".BO"]:
        yf_sym = f"{symbol}{suffix}"
        print(f"Trying {yf_sym}...")
        df = yf.download(yf_sym, period="1mo", progress=False)
        if not df.empty:
            print(f"✅ Found data for {yf_sym}!")
            print(df.tail(2))
            return True
        else:
            print(f"❌ No data for {yf_sym}")
    return False

if __name__ == "__main__":
    test_yf("ADVANCE")
