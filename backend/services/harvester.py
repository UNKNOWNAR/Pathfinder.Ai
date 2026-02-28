import hashlib
import threading
import requests
from flask import current_app
from models import db
from models.job import Job, HarvestLog

REMOTIVE_URL    = "https://remotive.com/api/remote-jobs"
ARBEITNOW_URL   = "https://arbeitnow.com/api/job-board-api"
JSEARCH_URL     = "https://jsearch.p.rapidapi.com/search"
JSEARCH_HOST    = "jsearch.p.rapidapi.com"

# ── Shared utilities ──────────────────────────────────────────────────────────
GLASSDOOR_MOCK = [
    {"title": "Senior Software Engineer",        "company": "Stripe",          "location": "San Francisco, CA", "url": "https://glassdoor.com"},
    {"title": "Backend Engineer (Python)",        "company": "Notion",          "location": "New York, NY",      "url": "https://glassdoor.com"},
    {"title": "Full Stack Developer",             "company": "Figma",           "location": "Remote",            "url": "https://glassdoor.com"},
    {"title": "Machine Learning Engineer",        "company": "OpenAI",          "location": "San Francisco, CA", "url": "https://glassdoor.com"},
    {"title": "DevOps Engineer",                  "company": "HashiCorp",       "location": "Remote",            "url": "https://glassdoor.com"},
    {"title": "Data Engineer",                    "company": "Databricks",      "location": "Amsterdam, NL",     "url": "https://glassdoor.com"},
    {"title": "Frontend Engineer (Vue/React)",    "company": "Linear",          "location": "Remote",            "url": "https://glassdoor.com"},
    {"title": "Cloud Infrastructure Engineer",   "company": "Cloudflare",      "location": "Austin, TX",        "url": "https://glassdoor.com"},
    {"title": "Site Reliability Engineer",        "company": "PagerDuty",       "location": "Remote",            "url": "https://glassdoor.com"},
    {"title": "iOS Engineer",                     "company": "Duolingo",        "location": "Pittsburgh, PA",    "url": "https://glassdoor.com"},
    {"title": "Android Engineer",                 "company": "Discord",         "location": "Remote",            "url": "https://glassdoor.com"},
    {"title": "Security Engineer",                "company": "Crowdstrike",     "location": "Sunnyvale, CA",     "url": "https://glassdoor.com"},
    {"title": "Platform Engineer",                "company": "Vercel",          "location": "Remote",            "url": "https://glassdoor.com"},
    {"title": "Staff Engineer, Infrastructure",  "company": "Shopify",         "location": "Remote",            "url": "https://glassdoor.com"},
    {"title": "Engineering Manager",             "company": "Atlassian",       "location": "Sydney, AU",        "url": "https://glassdoor.com"},
    {"title": "Product Engineer",                 "company": "Loom",            "location": "Remote",            "url": "https://glassdoor.com"},
    {"title": "Distributed Systems Engineer",    "company": "Cockroach Labs",  "location": "New York, NY",      "url": "https://glassdoor.com"},
    {"title": "API Platform Engineer",           "company": "Twilio",          "location": "Remote",            "url": "https://glassdoor.com"},
    {"title": "Data Scientist",                  "company": "Spotify",         "location": "Stockholm, SE",     "url": "https://glassdoor.com"},
    {"title": "Software Engineer, Payments",     "company": "Brex",            "location": "Remote",            "url": "https://glassdoor.com"},
]


# ── Shared utilities ──────────────────────────────────────────────────────────

def _make_hash(title: str, company: str) -> str:
    raw = f"{title.strip().lower()}|{company.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _insert_job(title, company, location, description, source, url):
    """Insert a single job if its hash doesn't already exist. Returns 1 if added, 0 if skipped."""
    if not title or not company:
        return 0
    job_hash = _make_hash(title, company)
    if Job.query.filter_by(hash=job_hash).first():
        return 0
    db.session.add(Job(
        title=title, company=company, location=location,
        description=description, source=source, url=url, hash=job_hash,
    ))
    return 1


# ── Source fetchers ───────────────────────────────────────────────────────────

def _fetch_remotive() -> list:
    res = requests.get(REMOTIVE_URL, timeout=15)
    res.raise_for_status()
    return res.json().get("jobs", [])


def _fetch_arbeitnow() -> list:
    res = requests.get(ARBEITNOW_URL, timeout=15)
    res.raise_for_status()
    return res.json().get("data", [])


def _fetch_jsearch(api_key: str) -> list:
    if not api_key:
        print("[Harvester] JSEARCH_API_KEY not set — skipping LinkedIn source.")
        return []
    res = requests.get(
        JSEARCH_URL,
        headers={
            "X-RapidAPI-Key":  api_key,
            "X-RapidAPI-Host": JSEARCH_HOST,
        },
        params={
            "query":     "software engineer",
            "num_pages": "2",
            "page":      "1",
            "date_posted": "month",
        },
        timeout=15,
    )
    res.raise_for_status()
    return res.json().get("data", [])


# ── Core harvest runner ───────────────────────────────────────────────────────

def _run_harvest(app):
    with app.app_context():
        log = HarvestLog(status="running", jobs_added=0)
        db.session.add(log)
        db.session.commit()

        try:
            jobs_added = 0
            jsearch_key = app.config.get("JSEARCH_API_KEY", "")

            # --- Remotive ---
            for item in _fetch_remotive():
                jobs_added += _insert_job(
                    title       = (item.get("title") or "").strip(),
                    company     = (item.get("company_name") or "").strip(),
                    location    = item.get("candidate_required_location") or "Remote",
                    description = item.get("description") or "",
                    source      = "Remotive",
                    url         = item.get("url") or "",
                )

            # --- Arbeitnow ---
            for item in _fetch_arbeitnow():
                jobs_added += _insert_job(
                    title       = (item.get("title") or "").strip(),
                    company     = (item.get("company_name") or "").strip(),
                    location    = item.get("location") or "Remote",
                    description = item.get("description") or "",
                    source      = "Arbeitnow",
                    url         = item.get("url") or "",
                )

            # --- Glassdoor (mock scrape) ---
            for item in GLASSDOOR_MOCK:
                jobs_added += _insert_job(
                    title       = item["title"],
                    company     = item["company"],
                    location    = item["location"],
                    description = "",
                    source      = "Glassdoor",
                    url         = item["url"],
                )

            # --- LinkedIn via JSearch (RapidAPI) ---
            for item in _fetch_jsearch(jsearch_key):
                jobs_added += _insert_job(
                    title       = (item.get("job_title") or "").strip(),
                    company     = (item.get("employer_name") or "").strip(),
                    location    = item.get("job_city") or item.get("job_country") or "Remote",
                    description = item.get("job_description") or "",
                    source      = "LinkedIn",
                    url         = item.get("job_apply_link") or "",
                )

            db.session.commit()
            log.status     = "completed"
            log.jobs_added = jobs_added
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            log.status = "failed"
            db.session.commit()
            print(f"[Harvester] Harvest failed: {e}")


# ── Public entry points ───────────────────────────────────────────────────────

def harvest_remotive_jobs(app):
    thread = threading.Thread(target=_run_harvest, args=(app,), daemon=True)
    thread.start()
    return thread


def harvest_arbeitnow_jobs(app):
    thread = threading.Thread(target=_run_harvest, args=(app,), daemon=True)
    thread.start()
    return thread


def harvest_all(app):
    """Single entry point that runs all three sources in one background thread."""
    thread = threading.Thread(target=_run_harvest, args=(app,), daemon=True)
    thread.start()
    return thread
