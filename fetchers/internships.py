import time
import requests
from config import INTERNSHIP_REPO

LISTINGS_URL = (
    f"https://raw.githubusercontent.com/{INTERNSHIP_REPO}/dev/.github/scripts/listings.json"
)


def fetch_new_listings(days_back: int = 1) -> list[dict]:
    """Pull internship listings posted in the last `days_back` days from SimplifyJobs' listings.json."""
    try:
        resp = requests.get(LISTINGS_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[internships] failed to fetch listings: {e}")
        return []

    cutoff = time.time() - days_back * 86400
    listings = []
    seen = set()

    for job in data:
        if not (job.get("active") and job.get("is_visible")):
            continue
        if job.get("date_posted", 0) < cutoff:
            continue

        # De-dupe repeated postings (same company + title).
        key = (job.get("company_name", "").strip(), job.get("title", "").strip())
        if key in seen:
            continue
        seen.add(key)

        locations = job.get("locations") or []
        listings.append({
            "company": job.get("company_name", "").strip(),
            "role": job.get("title", "").strip(),
            "location": ", ".join(locations) if locations else "N/A",
            "apply_url": job.get("url", ""),
            "date": time.strftime("%b %d", time.gmtime(job.get("date_posted", 0))),
        })

    listings.sort(key=lambda x: x["company"].lower())
    return listings[:25]
