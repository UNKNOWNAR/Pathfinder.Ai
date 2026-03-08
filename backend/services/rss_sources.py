import feedparser
import logging
import requests

logger = logging.getLogger(__name__)


def fetch_remoteok_jobs():

    url = "https://remoteok.com/remote-dev-jobs.rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        feed = feedparser.parse(res.content)
        
        jobs = []
        for entry in feed.entries:
            jobs.append({
                "title": entry.get("title"),
                "company": "RemoteOK",
                "location": "Remote",
                "description": entry.get("summary", ""),
                "url": entry.get("link")
            })

        logger.info(f"RemoteOK RSS fetched {len(jobs)} jobs")
        return jobs
    except Exception as e:
        logger.error(f"RemoteOK fetch failed: {e}")
        return []


def fetch_weworkremotely_jobs():

    url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"

    feed = feedparser.parse(url)

    jobs = []

    for entry in feed.entries:

        jobs.append({
            "title": entry.get("title"),
            "company": "WeWorkRemotely",
            "location": "Remote",
            "description": entry.get("summary", ""),
            "url": entry.get("link")
        })

    logger.info(f"WeWorkRemotely RSS fetched {len(jobs)} jobs")

    return jobs


def fetch_remotive_jobs():
    """Fetches jobs from Remotive's JSON API."""
    url = "https://remotive.com/api/remote-jobs?category=software-dev"
    try:
        res = requests.get(url, timeout=20)
        res.raise_for_status()
        data = res.json()
        raw_jobs = data.get("jobs", [])

        jobs = []
        for j in raw_jobs:
            jobs.append({
                "title": j.get("title"),
                "company": j.get("company_name"),
                "location": j.get("candidate_required_location", "Remote"),
                "description": j.get("description", ""),
                "url": j.get("url")
            })

        logger.info(f"Remotive API fetched {len(jobs)} jobs")
        return jobs
    except Exception as e:
        logger.error(f"Remotive fetch failed: {e}")
        return []
