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


def fetch_naukri_jobs():

    url = "https://www.naukri.com/code-360/jobs-feed"

    try:

        res = requests.get(url, timeout=10)

        feed = feedparser.parse(res.content)

        jobs = []

        for entry in feed.entries:

            jobs.append({
                "title": entry.get("title"),
                "company": "Naukri",
                "location": "India",
                "description": entry.get("summary", ""),
                "url": entry.get("link")
            })

        logger.info(f"Naukri RSS fetched {len(jobs)} jobs")

        return jobs

    except Exception as e:

        logger.error(f"Naukri RSS failed: {e}")

        return []


def fetch_indeed_jobs():

    url = "https://www.indeed.co.in/rss?q=software+engineer&l=India"

    feed = feedparser.parse(url)

    jobs = []

    for entry in feed.entries:

        jobs.append({
            "title": entry.get("title"),
            "company": "Indeed",
            "location": "India",
            "description": entry.get("summary", ""),
            "url": entry.get("link")
        })

    logger.info(f"Indeed RSS fetched {len(jobs)} jobs")

    return jobs


def fetch_stackoverflow_jobs():

    url = "https://stackoverflow.com/jobs/feed"

    feed = feedparser.parse(url)

    jobs = []

    for entry in feed.entries:

        jobs.append({
            "title": entry.get("title"),
            "company": "StackOverflow",
            "location": "Global",
            "description": entry.get("summary", ""),
            "url": entry.get("link")
        })

    logger.info(f"StackOverflow RSS fetched {len(jobs)} jobs")

    return jobs


def fetch_wellfound_jobs():

    url = "https://wellfound.com/jobs.rss"

    feed = feedparser.parse(url)

    jobs = []

    for entry in feed.entries:

        jobs.append({
            "title": entry.get("title"),
            "company": "Wellfound",
            "location": "Startup",
            "description": entry.get("summary", ""),
            "url": entry.get("link")
        })

    logger.info(f"Wellfound RSS fetched {len(jobs)} jobs")

    return jobs
