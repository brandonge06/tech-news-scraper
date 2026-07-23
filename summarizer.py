import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _call(prompt: str) -> str:
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def summarize_general_tech(articles: list[dict]) -> str:
    if not articles:
        return "No general tech news fetched today."
    blob = "\n".join(f"- [{a['source']}] {a['title']}: {a['summary'][:200]}" for a in articles)
    return _call(
        f"You are writing a concise daily tech digest for a software engineer. "
        f"Summarize the following tech headlines into 4–6 bullet points covering the most important stories. "
        f"Be specific — include company names, product names, and numbers where relevant. No fluff.\n\n{blob}"
    )


def summarize_ai(articles: list[dict]) -> str:
    if not articles:
        return "No AI news fetched today."
    blob = "\n".join(f"- [{a['source']}] {a['title']}: {a['summary'][:300]}" for a in articles)
    return _call(
        f"You are writing the AI & ML section of a daily tech digest for someone deeply interested in AI. "
        f"Summarize the following AI news into 5–8 bullet points. Go deeper than headlines — explain what's significant "
        f"about each development (new capability, benchmark, company move, research direction). Be specific.\n\n{blob}"
    )


def summarize_stocks(movers: list[dict]) -> str:
    if not movers:
        return "No stock data fetched today."
    blob = "\n".join(
        f"- {m['ticker']}: {'+' if m['change_pct'] >= 0 else ''}{m['change_pct']}% (${m['price']}). "
        f"News: {'; '.join(h['title'] for h in m['headlines']) or 'none'}"
        for m in movers
    )
    return _call(
        f"Summarize today's tech stock movements in 3–5 bullet points. "
        f"For each significant mover, mention the ticker, direction, and the likely reason based on the news. "
        f"Keep it factual and brief.\n\n{blob}"
    )


def format_internships(listings: list[dict]) -> str:
    if not listings:
        return "No new internship listings in the last 24 hours."
    lines = []
    for l in listings:
        apply_link = '<a href="' + l['apply_url'] + '">Apply</a>' if l['apply_url'] else ''
        lines.append(f"• <b>{l['company']}</b> — {l['role']} ({l['location']}) {apply_link}")
    return "\n".join(lines)


def format_sources(articles: list[dict], limit: int = 8) -> str:
    """Build a deduped, capped list of linked article titles to append under a summary."""
    if not articles:
        return ""
    # Round-robin across sources so no single outlet dominates the list.
    by_source = {}
    for a in articles:
        title = a.get("title", "").strip()
        url = a.get("url", "")
        if not title or not url:
            continue
        by_source.setdefault(a["source"], []).append(a)

    seen = set()
    lines = []
    while len(lines) < limit and any(by_source.values()):
        for source, queue in by_source.items():
            if not queue:
                continue
            a = queue.pop(0)
            title = a["title"].strip()
            if title in seen:
                continue
            seen.add(title)
            lines.append(f'• <a href="{a["url"]}">{title}</a> <span style="color:#aaa">— {source}</span>')
            if len(lines) >= limit:
                break
    return "\n".join(lines)


def format_stock_links(movers: list[dict]) -> str:
    """Build linked tickers (to Yahoo Finance) with their linked headlines."""
    if not movers:
        return ""
    lines = []
    for m in movers:
        sign = "+" if m["change_pct"] >= 0 else ""
        color = "#16a34a" if m["change_pct"] >= 0 else "#dc2626"
        ticker_link = f'<a href="https://finance.yahoo.com/quote/{m["ticker"]}">{m["ticker"]}</a>'
        head = ""
        if m["headlines"]:
            h = m["headlines"][0]
            head = f' — <a href="{h["url"]}">{h["title"]}</a>' if h["url"] else f' — {h["title"]}'
        lines.append(
            f'<b>{ticker_link}</b> '
            f'<span style="color:{color}">{sign}{m["change_pct"]}%</span> '
            f'(${m["price"]}){head}'
        )
    return "\n".join(lines)
