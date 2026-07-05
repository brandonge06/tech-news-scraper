import requests
import re
from datetime import datetime, timedelta
from config import INTERNSHIP_REPO


def fetch_new_listings(days_back: int = 1) -> list[dict]:
    """Pull internship listings added in the last `days_back` days from the SimplifyJobs README."""
    url = f"https://api.github.com/repos/{INTERNSHIP_REPO}/contents/README.md"
    headers = {"Accept": "application/vnd.github.v3.raw"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        content = resp.text
    except Exception as e:
        print(f"[internships] failed to fetch README: {e}")
        return []

    listings = []
    # Table rows look like: | Company | Role | Location | ... | Date |
    row_pattern = re.compile(r"^\|(.+)\|$", re.MULTILINE)
    cutoff = datetime.now() - timedelta(days=days_back)

    for match in row_pattern.finditer(content):
        cells = [c.strip() for c in match.group(1).split("|")]
        if len(cells) < 5:
            continue
        # Skip header and separator rows
        if "---" in cells[0] or cells[0].lower() in ("company", ""):
            continue

        company, role, location, apply, date_str = cells[0], cells[1], cells[2], cells[3], cells[-1]

        # Try to parse date (format varies: "Jun 20" or "2025-06-20")
        for fmt in ("%b %d", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(date_str.strip(), fmt)
                if fmt == "%b %d":
                    parsed = parsed.replace(year=datetime.now().year)
                if parsed >= cutoff:
                    listings.append({
                        "company": company,
                        "role": role,
                        "location": location,
                        "apply_url": re.search(r'\(([^)]+)\)', apply).group(1) if re.search(r'\(([^)]+)\)', apply) else "",
                        "date": date_str.strip(),
                    })
                break
            except ValueError:
                continue

    return listings[:20]
