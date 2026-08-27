import time
import requests
from config import INTERNSHIP_REPOS

LISTINGS_URL_TMPL = "https://raw.githubusercontent.com/{repo}/dev/.github/scripts/listings.json"


def _fetch_repo(repo: str) -> list[dict]:
    try:
        resp = requests.get(LISTINGS_URL_TMPL.format(repo=repo), timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[internships] failed to fetch listings from {repo}: {e}")
        return []


def fetch_new_listings(days_back: int = 1) -> list[dict]:
    """Pull internship listings posted in the last `days_back` days from SimplifyJobs' repos.

    Multiple term repos (e.g. Summer2026, Summer2027) are merged, since SimplifyJobs
    sometimes cross-lists the same posting in more than one repo.
    """
    cutoff = time.time() - days_back * 86400
    listings = []
    seen_ids = set()
    seen_keys = set()

    for repo in INTERNSHIP_REPOS:
        for job in _fetch_repo(repo):
            if not (job.get("active") and job.get("is_visible")):
                continue
            if job.get("date_posted", 0) < cutoff:
                continue

            # De-dupe listings that appear in more than one repo: prefer the
            # unique listing id when present, falling back to company + title + term.
            job_id = job.get("id")
            terms = job.get("terms") or []
            key = (job.get("company_name", "").strip(), job.get("title", "").strip(), tuple(terms))
            if job_id:
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            locations = job.get("locations") or []
            listings.append({
                "company": job.get("company_name", "").strip(),
                "role": job.get("title", "").strip(),
                "location": ", ".join(locations) if locations else "N/A",
                "apply_url": job.get("url", ""),
                "date": time.strftime("%b %d", time.gmtime(job.get("date_posted", 0))),
            })

    listings.sort(key=lambda x: x["company"].lower())
    return listings
