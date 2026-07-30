import requests

CONSTITUENTS_URL = (
    "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
)


def fetch_sp500_tickers() -> set[str]:
    """Current S&P 500 constituent tickers, symbol column of the datasets/s-and-p-500-companies CSV."""
    try:
        resp = requests.get(CONSTITUENTS_URL, timeout=15)
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()[1:]
        return {line.split(",")[0].strip().upper() for line in lines if line.strip()}
    except Exception as e:
        print(f"[sp500] failed to fetch constituents: {e}")
        return set()
