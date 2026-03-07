import logging
import requests
import threading

from models import db
from models.job import Job, HarvestLog
from services.utils import make_job_hash

from services.rss_sources import (
    fetch_remoteok_jobs,
    fetch_weworkremotely_jobs,
    fetch_naukri_jobs,
    fetch_wellfound_jobs
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


def is_india_or_remote(location):

    if not location:
        return False

    loc = location.lower()

    if "india" in loc:
        return True

    if "remote" in loc:
        return True

    for city in INDIA_CITIES:
        if city.lower() in loc:
            return True

    return False


def insert_jobs(source, raw_jobs, existing_hashes):

    inserted = 0
    new_jobs = []

    for job in raw_jobs:

        title = job.get("title")
        company = job.get("company")
        location = job.get("location")
        description = job.get("description", "")
        url = job.get("url")

        if not title or not company:
            continue

        if not is_india_or_remote(location):
            continue

        job_hash = make_job_hash(title, company, url or "")

        if job_hash in existing_hashes:
            continue

        new_job = Job(
            title=title,
            company=company,
            location=location,
            description=description,
            source=source,
            url=url,
            hash=job_hash
        )

        new_jobs.append(new_job)
        existing_hashes.add(job_hash)

    if new_jobs:

        db.session.bulk_save_objects(new_jobs)
        db.session.commit()

        inserted = len(new_jobs)

    logger.info(f"{source}: inserted {inserted} jobs")

    return inserted


def fetch_remotive():

    url = "https://remotive.com/api/remote-jobs"

    res = requests.get(url)

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

    res = requests.get(url)

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

    jobs = []

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    for city in INDIA_CITIES:

        query = f"software engineer {city}"

        logger.info(f"LinkedIn query: {query}")

        params = {
            "query": query,
            "page": "1",
            "num_pages": "1",
            "date_posted": "week"
        }

        res = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers=headers,
            params=params
        )

        data = res.json()

        for j in data.get("data", []):

            jobs.append({
                "title": j.get("job_title"),
                "company": j.get("employer_name"),
                "location": j.get("job_city") or j.get("job_country"),
                "description": j.get("job_description"),
                "url": j.get("job_apply_link")
            })

    logger.info(f"LinkedIn fetched {len(jobs)} jobs")

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
            ("RemoteOK", fetch_remoteok_jobs),
            ("WeWorkRemotely", fetch_weworkremotely_jobs),
            ("Naukri", fetch_naukri_jobs),
            ("Wellfound", fetch_wellfound_jobs),
        ]

        for name, fn in sources:

            try:

                logger.info(f"{name}: fetching")

                raw_jobs = fn()

                added = insert_jobs(name, raw_jobs, existing_hashes)

                total_added += added

            except Exception as e:

                logger.error(f"{name} FAILED: {e}")

                continue

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

    return harvest_all(app, roles, locations)