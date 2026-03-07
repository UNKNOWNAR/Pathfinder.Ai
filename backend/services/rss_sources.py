import feedparser
import logging

logger = logging.getLogger(__name__)


def fetch_remoteok_jobs():
    url = "https://remoteok.com/remote-dev-jobs.rss"
    feed = feedparser.parse(url)

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
    import feedparser
    import requests
    import logging

    logger = logging.getLogger(__name__)

    url = "https://www.naukri.com/code-360/jobs-feed"

    try:
        res = requests.get(url, timeout=5)
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
    

def fetch_wellfound_jobs():
    url = "https://wellfound.com/jobs.rss"
    feed = feedparser.parse(url)

    jobs = []

    for entry in feed.entries:
        jobs.append({
            "title": entry.get("title"),
            "company": "Wellfound",
            "location": "Remote",
            "description": entry.get("summary", ""),
            "url": entry.get("link")
        })

    logger.info(f"Wellfound RSS fetched {len(jobs)} jobs")
    return jobs