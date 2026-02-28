import hashlib
import threading
import requests
from models import db
from models.job import Job, HarvestLog

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"


def _make_hash(title: str, company: str) -> str:
    raw = f"{title.strip().lower()}|{company.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _fetch_remotive_jobs() -> list:
    response = requests.get(REMOTIVE_URL, timeout=15)
    response.raise_for_status()
    return response.json().get("jobs", [])


def _run_harvest(app):
    with app.app_context():
        log = HarvestLog(status="running", jobs_added=0)
        db.session.add(log)
        db.session.commit()

        try:
            raw_jobs = _fetch_remotive_jobs()

            jobs_added = 0
            for item in raw_jobs:
                title   = (item.get("title") or "").strip()
                company = (item.get("company_name") or "").strip()

                if not title or not company:
                    continue

                job_hash = _make_hash(title, company)

                if Job.query.filter_by(hash=job_hash).first():
                    continue

                job = Job(
                    title       = title,
                    company     = company,
                    location    = item.get("candidate_required_location") or "Remote",
                    description = item.get("description") or "",
                    source      = "Remotive",
                    url         = item.get("url") or "",
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
            print(f"[Harvester] Remotive harvest failed: {e}")


def harvest_remotive_jobs(app):
    """
    Spawns a background thread to harvest jobs from Remotive API
    without blocking the main Flask request thread.
    """
    thread = threading.Thread(target=_run_harvest, args=(app,), daemon=True)
    thread.start()
    return thread
