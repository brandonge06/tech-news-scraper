import yfinance as yf
from config import STOCK_TICKERS


def fetch_movers() -> list[dict]:
    results = []
    for ticker in STOCK_TICKERS:
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            history = t.history(period="2d")
            if len(history) < 2:
                continue

            prev_close = history["Close"].iloc[-2]
            curr_close = history["Close"].iloc[-1]
            pct_change = ((curr_close - prev_close) / prev_close) * 100

            news = t.news[:2] if t.news else []
            headlines = [n.get("content", {}).get("title", "") for n in news if n.get("content")]

            results.append({
                "ticker": ticker,
                "price": round(curr_close, 2),
                "change_pct": round(pct_change, 2),
                "headlines": headlines,
            })
        except Exception as e:
            print(f"[stocks] failed to fetch {ticker}: {e}")

    results.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return results
