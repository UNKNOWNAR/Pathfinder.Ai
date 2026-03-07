import logging
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

from models import db
from models.job import Job, HarvestLog
from services.utils import make_job_hash

from services.rss_sources import (
    fetch_remoteok_jobs,
    fetch_weworkremotely_jobs
)

logger = logging.getLogger(__name__)


INDIA_CITIES = [
    "Bangalore",
    "Hyderabad",
    "Pune",
    "Chennai",
    "Mumbai",
    "Delhi",
    "Gurgaon",
    "Noida",
    "Kolkata"
]


def is_allowed_location(location):

    if not location:
        return False

    loc = location.lower()

    allowed_words = [
        "india",
        "remote",
        "worldwide",
        "anywhere",
        "global"
    ]

    for w in allowed_words:
        if w in loc:
            return True

    for c in INDIA_CITIES:
        if c.lower() in loc:
            return True

    return False


def insert_jobs(source, raw_jobs, existing_hashes):

    new_jobs = []
    inserted = 0

    for job in raw_jobs:

        title = job.get("title")
        company = job.get("company")
        location = job.get("location")
        description = job.get("description", "")
        url = job.get("url")

        if not title or not company:
            continue

        if not is_allowed_location(location):
            continue

        job_hash = make_job_hash(title, company, url or "")

        if job_hash in existing_hashes:
            continue

        new_jobs.append(
            Job(
                title=title,
                company=company,
                location=location,
                description=description,
                source=source,
                url=url,
                hash=job_hash
            )
        )

        existing_hashes.add(job_hash)

    if new_jobs:

        db.session.bulk_save_objects(new_jobs)
        db.session.commit()

        inserted = len(new_jobs)

    logger.info(f"{source}: inserted {inserted} jobs")

    return inserted


def fetch_remotive():

    url = "https://remotive.com/api/remote-jobs"

    res = requests.get(url, timeout=20)

    data = res.json()

    jobs = []

    for j in data.get("jobs", []):

        jobs.append({
            "title": j.get("title"),
            "company": j.get("company_name"),
            "location": j.get("candidate_required_location"),
            "description": j.get("description"),
            "url": j.get("url")
        })

    logger.info(f"Remotive fetched {len(jobs)} jobs")

    return jobs


def fetch_arbeitnow():

    url = "https://arbeitnow.com/api/job-board-api"

    res = requests.get(url, timeout=20)

    data = res.json()

    jobs = []

    for j in data.get("data", []):

        jobs.append({
            "title": j.get("title"),
            "company": j.get("company_name"),
            "location": j.get("location"),
            "description": j.get("description"),
            "url": j.get("url")
        })

    logger.info(f"Arbeitnow fetched {len(jobs)} jobs")

    return jobs


def fetch_jsearch(api_key):

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    def fetch_city(city):

        query = f"software engineer {city}"

        logger.info(f"LinkedIn query: {query}")

        params = {
            "query": query,
            "page": "1",
            "num_pages": "1",
            "date_posted": "week"
        }

        try:

            res = requests.get(
                "https://jsearch.p.rapidapi.com/search",
                headers=headers,
                params=params,
                timeout=15
            )

            data = res.json()

            jobs = []

            for j in data.get("data", []):

                jobs.append({
                    "title": j.get("job_title"),
                    "company": j.get("employer_name"),
                    "location": j.get("job_city") or j.get("job_country"),
                    "description": j.get("job_description"),
                    "url": j.get("job_apply_link")
                })

            return jobs

        except Exception as e:

            logger.error(f"LinkedIn {city} failed: {e}")
            return []

    jobs = []

    with ThreadPoolExecutor(max_workers=4) as executor:

        results = executor.map(fetch_city, INDIA_CITIES)

        for r in results:
            jobs.extend(r)

    logger.info(f"LinkedIn fetched {len(jobs)} jobs")

    return jobs


def fetch_adzuna(app):

    app_id = app.config.get("ADZUNA_APP_ID")
    app_key = app.config.get("ADZUNA_APP_KEY")

    jobs = []

    for page in range(1, 6):

        url = f"https://api.adzuna.com/v1/api/jobs/in/search/{page}"

        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": 50,
            "what": "software engineer"
        }

        try:

            res = requests.get(url, params=params, timeout=15)

            data = res.json()

            for j in data.get("results", []):

                jobs.append({
                    "title": j.get("title"),
                    "company": j.get("company", {}).get("display_name"),
                    "location": j.get("location", {}).get("display_name"),
                    "description": j.get("description"),
                    "url": j.get("redirect_url")
                })

        except Exception as e:

            logger.error(f"Adzuna page {page} failed: {e}")

    logger.info(f"Adzuna fetched {len(jobs)} jobs")

    return jobs


def _run_harvest(app):

    with app.app_context():

        logger.info("MASTER HARVEST STARTED")

        log = HarvestLog(source="all", status="running", jobs_added=0)

        db.session.add(log)
        db.session.commit()

        existing_hashes = {h[0] for h in db.session.query(Job.hash).all()}

        total_added = 0

        sources = [

            ("Remotive", fetch_remotive),
            ("Arbeitnow", fetch_arbeitnow),
            ("LinkedIn", lambda: fetch_jsearch(app.config.get("JSEARCH_API_KEY"))),
            ("Adzuna", lambda: fetch_adzuna(app)),
            ("RemoteOK", fetch_remoteok_jobs),
            ("WeWorkRemotely", fetch_weworkremotely_jobs)
        ]

        for name, fn in sources:

            try:

                logger.info(f"{name}: fetching")

                raw_jobs = fn()

                added = insert_jobs(name, raw_jobs, existing_hashes)

                total_added += added

            except Exception as e:

                logger.error(f"{name} FAILED: {e}")

        log.status = "completed"
        log.jobs_added = total_added

        db.session.commit()

        logger.info(f"HARVEST COMPLETE — added {total_added} jobs")


def harvest_all(app, roles=None, locations=None):

    thread = threading.Thread(
        target=_run_harvest,
        args=(app,),
        daemon=True
    )

    thread.start()

    return thread


def harvest_source(app, source, roles=None, locations=None):

    return harvest_all(app)