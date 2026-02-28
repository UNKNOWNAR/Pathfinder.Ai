import hashlib
import threading
import requests
from flask import current_app
from models import db
from models.job import Job, HarvestLog

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"
ADZUNA_COUNTRY  = "gb"   # 'gb', 'us', 'au', etc. — configurable
ADZUNA_RESULTS  = 50     # results per page (Adzuna max is 50)


def _make_hash(title: str, company: str) -> str:
    raw = f"{title.strip().lower()}|{company.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _fetch_adzuna_page(app_id: str, app_key: str, page: int = 1) -> list:
    url = f"{ADZUNA_BASE_URL}/{ADZUNA_COUNTRY}/search/{page}"
    params = {
        "app_id":        app_id,
        "app_key":       app_key,
        "results_per_page": ADZUNA_RESULTS,
        "content-type":  "application/json",
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json().get("results", [])


def _run_harvest(app):
    with app.app_context():
        log = HarvestLog(status="running", jobs_added=0)
        db.session.add(log)
        db.session.commit()

        try:
            app_id  = app.config.get("ADZUNA_APP_ID", "")
            app_key = app.config.get("ADZUNA_APP_KEY", "")

            if not app_id or not app_key:
                raise ValueError("ADZUNA_APP_ID or ADZUNA_APP_KEY not configured.")

            raw_jobs = _fetch_adzuna_page(app_id, app_key, page=1)

            jobs_added = 0
            for item in raw_jobs:
                title   = item.get("title", "").strip()
                company = item.get("company", {}).get("display_name", "").strip()

                if not title or not company:
                    continue

                job_hash = _make_hash(title, company)

                # Skip if already in DB (idempotent insert)
                if Job.query.filter_by(hash=job_hash).first():
                    continue

                job = Job(
                    title       = title,
                    company     = company,
                    location    = item.get("location", {}).get("display_name", ""),
                    description = item.get("description", ""),
                    source      = "Adzuna",
                    url         = item.get("redirect_url", ""),
                    hash        = job_hash,
                )
                db.session.add(job)
                jobs_added += 1

            db.session.commit()

            log.status     = "completed"
            log.jobs_added = jobs_added
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            log.status = "failed"
            db.session.commit()
            print(f"[Harvester] Error during Adzuna harvest: {e}")


def harvest_adzuna_jobs(app):
    """
    Spawns a background thread to harvest jobs from Adzuna without
    blocking the main Flask request thread.
    """
    thread = threading.Thread(target=_run_harvest, args=(app,), daemon=True)
    thread.start()
    return thread
