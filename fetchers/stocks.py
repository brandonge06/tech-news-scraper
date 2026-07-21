from typing import Optional
import yfinance as yf
from config import STOCK_TICKERS

# How many dynamic movers to pull from each screener before deduping.
SCREENER_COUNT = 15
# Final number of stocks to include in the digest.
TOP_N = 8


def _dynamic_symbols() -> list[str]:
    """Pull today's trending symbols live from Yahoo's screeners."""
    symbols = []
    for screener in ("most_actives", "day_gainers", "day_losers"):
        try:
            result = yf.screen(screener, count=SCREENER_COUNT)
            for q in result.get("quotes", []):
                sym = q.get("symbol")
                if sym:
                    symbols.append(sym)
        except Exception as e:
            print(f"[stocks] screener '{screener}' failed: {e}")
    return symbols


def _fetch_one(ticker: str) -> Optional[dict]:
    try:
        t = yf.Ticker(ticker)
        history = t.history(period="2d")
        if len(history) < 2:
            return None

        prev_close = history["Close"].iloc[-2]
        curr_close = history["Close"].iloc[-1]
        pct_change = ((curr_close - prev_close) / prev_close) * 100

        news = t.news[:2] if t.news else []
        headlines = [n.get("content", {}).get("title", "") for n in news if n.get("content")]

        return {
            "ticker": ticker,
            "price": round(curr_close, 2),
            "change_pct": round(pct_change, 2),
            "headlines": headlines,
        }
    except Exception as e:
        print(f"[stocks] failed to fetch {ticker}: {e}")
        return None


def fetch_movers() -> list[dict]:
    # Watchlist tickers are always included; trending symbols are pulled live.
    watchlist = [t.strip().upper() for t in STOCK_TICKERS if t.strip()]
    trending = _dynamic_symbols()

    # Dedupe while preserving order, watchlist first.
    seen = set()
    ordered = []
    for sym in watchlist + trending:
        if sym not in seen:
            seen.add(sym)
            ordered.append(sym)

    results = [r for r in (_fetch_one(sym) for sym in ordered) if r]

    # Always keep watchlist names, then fill remaining slots with the biggest movers.
    watch_results = [r for r in results if r["ticker"] in watchlist]
    other_results = sorted(
        (r for r in results if r["ticker"] not in watchlist),
        key=lambda x: abs(x["change_pct"]),
        reverse=True,
    )

    # Watchlist always included; fill remaining slots with the biggest movers.
    remaining = max(0, TOP_N - len(watch_results))
    combined = watch_results + other_results[:remaining]
    combined.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return combined
