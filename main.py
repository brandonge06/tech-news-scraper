from datetime import datetime
from fetchers.rss import fetch_all
from fetchers.stocks import fetch_movers
from fetchers.internships import fetch_new_listings
from summarizer import summarize_general_tech, summarize_ai, summarize_stocks, format_internships
from emailer import send_digest


def run():
    date = datetime.now().strftime("%A, %B %-d %Y")
    print(f"[main] running TechPulse digest for {date}")

    print("[main] fetching RSS feeds...")
    general_articles = fetch_all("general")
    ai_articles = fetch_all("ai")

    print("[main] fetching stock data...")
    movers = fetch_movers()

    print("[main] fetching internship listings...")
    internships = fetch_new_listings(days_back=1)

    print("[main] summarizing with Claude...")
    tech_summary = summarize_general_tech(general_articles)
    ai_summary = summarize_ai(ai_articles)
    stock_summary = summarize_stocks(movers)
    internship_html = format_internships(internships)

    print("[main] sending email...")
    send_digest(date, tech_summary, ai_summary, stock_summary, internship_html)
    print("[main] done.")


if __name__ == "__main__":
    run()
