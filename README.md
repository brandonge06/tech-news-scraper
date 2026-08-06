# TechPulse — Daily Tech News Digest

A scheduled Python pipeline that scrapes tech news, internship listings, and trending stocks, summarizes everything with Claude AI, and delivers a clean HTML email digest every morning.

---

## What It Does

Each morning, TechPulse:

1. Pulls articles from curated RSS feeds across general tech and AI sources
2. Scrapes the [SimplifyJobs Summer 2027 internship board](https://github.com/SimplifyJobs/Summer2027-Internships) for new listings
3. Fetches top tech stock movers and their news headlines
4. Sends everything through Claude to produce tight, readable summaries
5. Composes and delivers a formatted HTML email to your inbox

The email is structured in three sections: a general tech digest, a deeper AI-focused section, and a combined internships + market movers section at the bottom.

---

## Tech Stack

### Language — Python 3.11+

**Why:** Python is the unambiguous choice for a data pipeline like this. The ecosystem is unmatched — `feedparser`, `yfinance`, `beautifulsoup4`, and the Anthropic SDK are all Python-native and actively maintained. Gluing HTTP calls, parsing, an LLM API, and email delivery together is where Python thrives.

**Alternatives considered:**
- **Node.js** — good async I/O, but the data science and scraping ecosystem is weaker. `rss-parser` exists but `feedparser` is more battle-tested. Not worth the tradeoff.
- **Go** — fast and great for concurrent fetching, but the library ecosystem for this use case (RSS, finance, LLM clients) is thin. You'd be writing a lot more from scratch.

---

### RSS Parsing — `feedparser`

**Why:** `feedparser` is the gold standard for RSS/Atom parsing in Python. It handles malformed feeds gracefully, normalizes inconsistent date formats across sources, and abstracts away the differences between RSS 2.0, Atom, and RDF feeds. Zero configuration for any well-formed feed.

**Pros:**
- Handles every RSS/Atom variant without configuration
- Graceful degradation on malformed feeds (doesn't crash)
- Actively maintained since 2002, extremely stable

**Cons:**
- Synchronous only — no async support, so fetching many feeds blocks
- No built-in rate limiting or retry logic

**Alternatives considered:**
- **Raw `requests` + `BeautifulSoup`** — more control, but you're reimplementing what `feedparser` already does well. More code, more bugs.
- **`aiohttp` + custom XML parser** — would give you concurrent feed fetching, but async complexity isn't worth it for a daily cron job fetching ~10 feeds.

---

### Web Scraping — `requests` + `BeautifulSoup4`

Used specifically for the GitHub internship list and any non-RSS sources.

**Why:** The internship board (`SimplifyJobs/Summer2027-Internships`) is a GitHub README — plain HTML, server-rendered, and publicly accessible. `requests` + `bs4` is the right tool: simple, lightweight, no browser required.

**Pros:**
- Minimal overhead — no browser process, no JavaScript engine
- Fast for static/server-rendered pages
- `BeautifulSoup` handles malformed HTML well

**Cons:**
- Cannot execute JavaScript — useless for SPAs or heavily dynamic pages
- GitHub's CDN may rate-limit aggressive scrapers

**Alternatives considered:**
- **Playwright / Selenium** — full browser automation, handles JS. Massive overkill for a GitHub markdown page. Slow and resource-heavy.
- **Scrapy** — a full scraping framework. Overkill for two or three target URLs. Adds significant complexity and a learning curve.
- **GitHub API** — the cleaner approach, and we actually use it for the raw markdown file to avoid scraping HTML at all.

---

### Stock Data — `yfinance`

**Why:** `yfinance` wraps Yahoo Finance's unofficial API and returns clean pandas DataFrames. It's free, requires no API key for basic usage, and is the de facto standard for retail-level financial data in Python.

**Pros:**
- Completely free, no API key required
- Returns clean structured data (DataFrames)
- Supports historical prices, real-time quotes, news headlines, and top movers

**Cons:**
- Unofficial wrapper — Yahoo can change their underlying API without notice and break `yfinance`
- Not suitable for production trading systems; fine for a personal digest
- Rate limits exist but are generous for personal use

Both the watchlist (`STOCK_TICKERS`) and the live trending screener are filtered down to current S&P 500 constituents (`fetchers/sp500.py`, pulled from [datasets/s-and-p-500-companies](https://github.com/datasets/s-and-p-500-companies)) so the digest never surfaces small/micro-cap tickers outside the index.

**Alternatives considered:**
- **Alpha Vantage** — free tier is limited to 25 requests/day, which is too tight when fetching data on multiple tickers plus news
- **Polygon.io** — excellent API, but paid. No free tier for real-time data.
- **Finnhub** — generous free tier (60 req/min), solid alternative. Kept `yfinance` because it's simpler and handles top-movers queries natively.

---

### AI Summarization — Anthropic Claude API (`claude-haiku-4-5`)

**Why:** The core value of this project is not fetching news — it's condensing 50+ articles into a 5-minute read. Claude Haiku is purpose-built for this: it's fast, cheap (~$0.25/1M input tokens), and produces clean, structured summaries. We use Haiku for volume (bulk article summarization) and can optionally bump to Sonnet for the AI section if you want deeper analysis.

**Pros:**
- Best-in-class summarization quality
- Structured output support — can return JSON for consistent email formatting
- Fast (Haiku returns in ~1–2 seconds per call)
- Cost: a full daily run costs well under $0.05

**Cons:**
- Requires an API key and has a cost (small)
- Adds a network dependency — if Anthropic's API is down, the digest fails

**Alternatives considered:**
- **OpenAI GPT-4o-mini** — comparable cost and quality. No strong reason to prefer it here; Claude's summarization tends to be tighter and less verbose.
- **Local LLM via Ollama** — free, runs offline. Quality gap is significant for summarization tasks. Requires a machine with enough RAM to run a 7B+ model. Not worth the complexity for a personal tool.
- **No LLM — just headlines** — defeats the purpose. The whole point is synthesis, not aggregation.

---

### Email Delivery — `smtplib` (Gmail SMTP) + `email.mime`

**Why:** `smtplib` is part of the Python standard library — zero additional dependencies. For a personal digest to one recipient (yourself), Gmail SMTP is perfectly reliable and free.

**Pros:**
- No external service dependency
- Free forever
- HTML email support via `email.mime.multipart`

**Cons:**
- Gmail requires an App Password (2FA must be enabled)
- Not suitable for bulk sending — Gmail throttles at ~500 emails/day
- Deliverability can be inconsistent (may land in spam initially)

**Alternatives considered:**
- **SendGrid** — better deliverability, generous free tier (100 emails/day). Good choice if you want to send to multiple recipients or care about open tracking. Overkill for a personal digest.
- **Resend** — modern API, great DX, 3,000 free emails/month. Strong alternative if Gmail SMTP proves annoying to configure.
- **Mailgun** — similar to SendGrid, adds unnecessary complexity for one recipient.

---

### Scheduling — `cron` (system crontab)

**Why:** A daily email digest is a simple, time-based job. Cron is the right tool — it's universal, zero dependencies, and has been reliable for 50 years.

**Pros:**
- Zero dependencies, available on every Unix system
- Completely transparent — you can see exactly when it runs
- Doesn't require a running Python process

**Cons:**
- Your machine must be on and awake at the scheduled time
- No built-in retry on failure
- Logs require manual setup

**Alternatives considered:**
- **GitHub Actions** — runs in the cloud so your machine doesn't need to be on. Free for public repos. Good upgrade path if the cron approach is unreliable.
- **APScheduler** — Python-native scheduler. Requires a persistent Python process, which is more complexity than a daily job needs.
- **Celery + Redis** — serious distributed task queue. Extreme overkill.

---

### Configuration — `python-dotenv` + `.env`

Standard pattern. API keys and credentials live in `.env`, never committed. `python-dotenv` loads them into environment variables at runtime.

---

## Project Structure

```
news-scraper/
├── main.py                  # Entrypoint — orchestrates the full pipeline
├── config.py                # Loads and validates env vars
├── fetchers/
│   ├── rss.py               # RSS feed fetching and parsing
│   ├── stocks.py            # yfinance stock data and news
│   └── internships.py       # GitHub internship board scraper
├── summarizer.py            # Claude API calls for summarization
├── emailer.py               # HTML email composition and delivery
├── templates/
│   └── digest.html          # Jinja2 HTML email template
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/brandonge/news-scraper.git
cd news-scraper
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Gmail SMTP
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx   # Generate at myaccount.google.com/apppasswords
RECIPIENT_EMAIL=you@gmail.com

# Optional: stock tickers to track (comma-separated, must be S&P 500 members)
STOCK_TICKERS=AAPL,MSFT,NVDA,GOOGL,META,TSLA
```

> **Gmail App Password:** Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords). You must have 2FA enabled. Generate a password for "Mail".

### 3. Run manually

```bash
python main.py
```

### 4. Schedule with cron

Run `crontab -e` and add:

```cron
0 7 * * * /path/to/venv/bin/python /path/to/news-scraper/main.py >> /path/to/news-scraper/logs/cron.log 2>&1
```

This runs every day at 7:00 AM. Adjust the time to your preference.

---

## RSS Sources

### General Tech
| Source | Feed URL |
|---|---|
| Hacker News Top | `https://news.ycombinator.com/rss` |
| TechCrunch | `https://techcrunch.com/feed/` |
| The Verge | `https://www.theverge.com/rss/index.xml` |
| Ars Technica | `https://feeds.arstechnica.com/arstechnica/index` |
| Wired | `https://www.wired.com/feed/rss` |

### AI / ML Focus
| Source | Feed URL |
|---|---|
| MIT Technology Review (AI) | `https://www.technologyreview.com/topic/artificial-intelligence/feed` |
| The Batch (DeepLearning.AI) | `https://read.deeplearning.ai/the-batch/rss/` |
| Google DeepMind Blog | `https://deepmind.google/blog/rss.xml` |
| Hugging Face Blog | `https://huggingface.co/blog/feed.xml` |
| Import AI (Jack Clark) | `https://jack-clark.net/feed/` |

---

## Email Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TechPulse — Friday, June 20
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📰 TECH DIGEST
  3–5 sentence summary of the biggest general tech stories today

🤖 AI & ML SPOTLIGHT
  Deeper coverage: model releases, research papers, company moves

💼 INTERNSHIP BOARD
  New listings added to SimplifyJobs in the last 24 hours

📈 MARKET MOVERS
  Top tech stock gainers/losers + one-line news context per ticker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Cost Estimate

| Component | Cost |
|---|---|
| Claude Haiku (summarization) | ~$0.01–0.05/day |
| Gmail SMTP | Free |
| yfinance | Free |
| RSS feeds | Free |
| **Total** | **< $1.50/month** |

---

## Roadmap

- [ ] Core pipeline (RSS + Claude + email)
- [ ] Stock data integration
- [ ] Internship board scraper
- [ ] HTML email template
- [ ] Cron scheduling
- [ ] GitHub Actions fallback (cloud scheduling)
- [ ] Topic filtering / keyword prioritization
- [ ] Digest archive (save past emails locally)

---

## License

MIT
